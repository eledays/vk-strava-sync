package org.gadgetbridge.workoutsync.data

import android.content.Context
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore("settings")
data class Settings(
    val folderUri: String = "", val baseUrl: String = "", val token: String = "",
    val automatic: Boolean = false, val intervalMinutes: Long = 60,
    val lastAttempt: Long? = null, val lastSuccess: Long? = null, val lastResult: String = "Ещё не запускалась",
) { val configured get() = folderUri.isNotBlank() && baseUrl.isNotBlank() && token.isNotBlank() }

class SettingsRepository(private val context: Context) {
    private object K { val folder=stringPreferencesKey("folder"); val url=stringPreferencesKey("url"); val token=stringPreferencesKey("token"); val auto=booleanPreferencesKey("auto"); val interval=longPreferencesKey("interval"); val attempt=longPreferencesKey("attempt"); val success=longPreferencesKey("success"); val result=stringPreferencesKey("result") }
    val settings: Flow<Settings> = context.dataStore.data.map { p -> Settings(p[K.folder]?:"", p[K.url]?:"", p[K.token]?:"", p[K.auto]?:false, p[K.interval]?:60, p[K.attempt], p[K.success], p[K.result]?:"Ещё не запускалась") }
    suspend fun save(value: Settings) = context.dataStore.edit { p -> p[K.folder]=value.folderUri; p[K.url]=value.baseUrl.trimEnd('/'); p[K.token]=value.token; p[K.auto]=value.automatic; p[K.interval]=value.intervalMinutes }
    suspend fun recordAttempt(at: Long, result: String, successful: Boolean) = context.dataStore.edit { p -> p[K.attempt]=at; p[K.result]=result; if(successful) p[K.success]=at }
}

object UrlValidator {
    fun error(url: String, allowLocalHttp: Boolean): String? {
      return try {
        if (url.any(Char::isWhitespace)) "URL не должен содержать пробелы" else {
        val parsed = java.net.URI(url)
        if (parsed.host.isNullOrBlank()) "Укажите корректный адрес сервера"
        else if (parsed.rawQuery?.contains("token", ignoreCase=true) == true) "Не передавайте токен в URL"
        else if (parsed.scheme == "https") null
        else if (allowLocalHttp && parsed.scheme == "http" && (parsed.host == "localhost" || parsed.host == "127.0.0.1" || parsed.host == "10.0.2.2")) null
        else "Требуется HTTPS"
        }
      } catch (_: Exception) { "Укажите корректный адрес сервера" }
    }
}
