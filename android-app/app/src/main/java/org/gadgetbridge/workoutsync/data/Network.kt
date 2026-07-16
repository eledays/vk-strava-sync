package org.gadgetbridge.workoutsync.data

import android.content.ContentResolver
import android.net.Uri
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody
import okio.BufferedSink
import okio.source
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.http.*
import java.io.IOException
import java.net.*

@Serializable data class UploadResponse(val status: String, val message: String? = null)
interface WorkoutApi {
    @Multipart @POST suspend fun upload(@Url url:String, @Header("Authorization") auth:String, @Header("X-File-SHA256") hash:String, @Part file:MultipartBody.Part, @Part("sha256") hashPart:RequestBody, @Part("filename") filename:RequestBody, @Part("modifiedAt") modifiedAt:RequestBody?): Response<ResponseBody>
    @GET suspend fun health(@Url url:String): Response<ResponseBody>
}

class StreamingUriRequestBody(private val resolver:ContentResolver, private val uri:Uri, private val type:String?, private val length:Long?):RequestBody() {
    override fun contentType()=type?.toMediaTypeOrNull() ?: "application/octet-stream".toMediaType()
    override fun contentLength()=length ?: -1
    override fun writeTo(sink:BufferedSink) { resolver.openInputStream(uri)?.use { input -> sink.writeAll(input.source()) } ?: throw IOException("Файл больше недоступен") }
}

enum class ErrorKind { RETRY, PERMANENT }
data class ClassifiedError(val kind:ErrorKind,val message:String)
object NetworkErrorClassifier {
    fun http(code:Int)=when(code) {
        408,425,429, in 500..599 -> ClassifiedError(ErrorKind.RETRY,"Временная ошибка сервера (HTTP $code)")
        401,403 -> ClassifiedError(ErrorKind.PERMANENT,"Сервер отклонил токен авторизации. Проверьте настройки.")
        413 -> ClassifiedError(ErrorKind.PERMANENT,"Файл превышает допустимый размер на сервере.")
        415 -> ClassifiedError(ErrorKind.PERMANENT,"Сервер не поддерживает формат этого файла.")
        in 400..499 -> ClassifiedError(ErrorKind.PERMANENT,"Сервер отклонил запрос (HTTP $code)")
        else -> ClassifiedError(ErrorKind.RETRY,"Неожиданный ответ сервера (HTTP $code)")
    }
    fun exception(e:Throwable)=when(e) {
        is UnknownHostException -> ClassifiedError(ErrorKind.RETRY,"Не удалось найти сервер")
        is SocketTimeoutException -> ClassifiedError(ErrorKind.RETRY,"Истекло время ожидания сервера")
        is ConnectException, is SocketException -> ClassifiedError(ErrorKind.RETRY,"Соединение прервано")
        is IOException -> ClassifiedError(ErrorKind.RETRY,"Ошибка сети")
        else -> ClassifiedError(ErrorKind.PERMANENT,"Внутренняя ошибка: ${e.javaClass.simpleName}")
    }
}

sealed interface UploadOutcome { data class Success(val code:Int):UploadOutcome; data class Error(val classified:ClassifiedError,val code:Int?=null):UploadOutcome }
class UploadClient(private val resolver:ContentResolver) {
    private val api=Retrofit.Builder().baseUrl("https://localhost/").client(OkHttpClient.Builder().callTimeout(java.time.Duration.ofMinutes(5)).build()).build().create(WorkoutApi::class.java)
    private val json=Json { ignoreUnknownKeys=true }
    suspend fun upload(settings:Settings,file:WorkoutFileEntity):UploadOutcome = try {
        val body=StreamingUriRequestBody(resolver,Uri.parse(file.uri),file.mimeType,file.sizeBytes)
        val part=MultipartBody.Part.createFormData("file",file.fileName,body); val text="text/plain".toMediaType()
        val response=api.upload(settings.baseUrl.trimEnd('/')+"/api/v1/workouts","Bearer ${settings.token}",file.sha256,part,file.sha256.toRequestBody(text),file.fileName.toRequestBody(text),file.modifiedAt?.toString()?.toRequestBody(text))
        if(response.code() in listOf(200,201)) UploadOutcome.Success(response.code())
        else if(response.code()==409) {
            val parsed=runCatching { json.decodeFromString<UploadResponse>(response.errorBody()?.string().orEmpty()) }.getOrNull()
            if(parsed?.status=="already_processed") UploadOutcome.Success(409) else UploadOutcome.Error(NetworkErrorClassifier.http(409),409)
        } else UploadOutcome.Error(NetworkErrorClassifier.http(response.code()),response.code())
    } catch(e:Throwable) { UploadOutcome.Error(NetworkErrorClassifier.exception(e)) }
}
