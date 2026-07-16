package org.gadgetbridge.workoutsync.data

import android.content.Context
import android.net.Uri
import androidx.documentfile.provider.DocumentFile
import java.io.InputStream
import java.security.MessageDigest

object WorkoutFileFilter { fun supports(name: String) = name.substringAfterLast('.', "").lowercase() in setOf("fit", "gpx") }
object Sha256Calculator {
    fun calculate(input: InputStream): String = input.use { stream ->
        val digest=MessageDigest.getInstance("SHA-256"); val buffer=ByteArray(DEFAULT_BUFFER_SIZE)
        while(true) { val n=stream.read(buffer); if(n < 0) break; digest.update(buffer,0,n) }
        digest.digest().joinToString("") { "%02x".format(it) }
    }
}
sealed interface ScanResult { data class Found(val files: List<WorkoutFileEntity>): ScanResult; data class AccessLost(val message:String): ScanResult }

class DocumentTreeScanner(private val context: Context) {
    fun scan(uriText: String, now: Long = System.currentTimeMillis()): ScanResult {
        val uri=runCatching { Uri.parse(uriText) }.getOrNull() ?: return ScanResult.AccessLost("Повреждённый URI папки")
        val permitted=context.contentResolver.persistedUriPermissions.any { it.uri == uri && it.isReadPermission }
        if(!permitted) return ScanResult.AccessLost("Доступ к папке потерян. Выберите папку заново.")
        val root=DocumentFile.fromTreeUri(context,uri) ?: return ScanResult.AccessLost("Папка недоступна")
        if(!root.exists() || !root.isDirectory) return ScanResult.AccessLost("Папка недоступна")
        val found=mutableListOf<WorkoutFileEntity>(); val stack=ArrayDeque<DocumentFile>(); stack.add(root)
        try { while(stack.isNotEmpty()) for(file in stack.removeLast().listFiles()) {
            if(file.isDirectory) stack.add(file) else if(file.isFile && WorkoutFileFilter.supports(file.name.orEmpty())) {
                val size=file.length(); val modified=file.lastModified().takeIf { it > 0 }
                if(size <= 0 || (modified != null && now-modified < 30_000)) continue
                val hash=context.contentResolver.openInputStream(file.uri)?.let(Sha256Calculator::calculate) ?: continue
                found += WorkoutFileEntity(sha256=hash,uri=file.uri.toString(),fileName=file.name?:"workout",mimeType=file.type,sizeBytes=size,modifiedAt=modified,discoveredAt=now)
            }
        }} catch(_: SecurityException) { return ScanResult.AccessLost("Доступ к папке потерян. Выберите папку заново.") }
        return ScanResult.Found(found)
    }
}
