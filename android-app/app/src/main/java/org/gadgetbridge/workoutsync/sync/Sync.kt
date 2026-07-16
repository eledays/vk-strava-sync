package org.gadgetbridge.workoutsync.sync

import android.app.*
import android.content.Context
import androidx.core.app.NotificationCompat
import androidx.work.*
import kotlinx.coroutines.flow.first
import org.gadgetbridge.workoutsync.*
import org.gadgetbridge.workoutsync.data.*
import java.util.concurrent.TimeUnit

data class SyncSummary(val uploaded:Int,val temporary:Int,val permanent:Int) { val shouldRetry get()=temporary>0; val text get()="Отправлено: $uploaded, временных ошибок: $temporary, постоянных: $permanent" }
object WorkerResultPolicy { fun result(configurationValid:Boolean, internalFailure:Boolean, temporaryErrors:Boolean)= when { !configurationValid||internalFailure -> "failure"; temporaryErrors -> "retry"; else -> "success" } }

class SyncEngine(private val app:WorkoutSyncApp) {
    suspend fun run(): Pair<SyncSummary,String?> {
        val settings=app.settings.settings.first(); val now=System.currentTimeMillis()
        if(!settings.configured) return SyncSummary(0,0,0) to "Настройка не завершена"
        app.db.workoutFiles().recoverInterrupted()
        when(val scan=app.scanner.scan(settings.folderUri,now)) {
            is ScanResult.AccessLost -> return SyncSummary(0,0,0) to scan.message
            is ScanResult.Found -> scan.files.forEach { app.db.workoutFiles().insert(it) }
        }
        var ok=0; var retry=0; var permanent=0
        for(file in app.db.workoutFiles().queue()) {
            if(app.db.workoutFiles().claim(file.id,System.currentTimeMillis()) != 1) continue
            when(val result=app.uploader.upload(settings,file)) {
                is UploadOutcome.Success -> { app.db.workoutFiles().success(file.id,System.currentTimeMillis(),result.code); ok++ }
                is UploadOutcome.Error -> if(result.classified.kind==ErrorKind.RETRY) { app.db.workoutFiles().retry(file.id,result.code,result.classified.message); retry++ } else { app.db.workoutFiles().permanent(file.id,result.code,result.classified.message); permanent++ }
            }
        }
        return SyncSummary(ok,retry,permanent) to null
    }
}

class SyncWorker(context:Context,params:WorkerParameters):CoroutineWorker(context,params) {
    override suspend fun doWork():Result {
        val app=applicationContext as WorkoutSyncApp; val now=System.currentTimeMillis()
        return try {
            val (summary,configurationError)=SyncEngine(app).run()
            val text=configurationError ?: summary.text; app.settings.recordAttempt(now,text,configurationError==null&&!summary.shouldRetry)
            if(configurationError!=null) { app.notifications.error(configurationError); Result.failure() }
            else { app.notifications.summary(summary); if(summary.shouldRetry) Result.retry() else Result.success() }
        } catch(e:Exception) { app.settings.recordAttempt(now,"Внутренняя ошибка",false); Result.failure() }
    }
}

object SyncScheduler {
    const val PERIODIC="periodic_workout_sync"; const val MANUAL="manual_workout_sync"
    val intervals=listOf(15L,30L,60L,180L,360L,720L,1440L)
    private fun constraints()=Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build()
    fun configure(context:Context,enabled:Boolean,minutes:Long) { val wm=WorkManager.getInstance(context); if(!enabled) wm.cancelUniqueWork(PERIODIC) else { val req=PeriodicWorkRequestBuilder<SyncWorker>(minutes.coerceAtLeast(15),TimeUnit.MINUTES).setConstraints(constraints()).setBackoffCriteria(BackoffPolicy.EXPONENTIAL,30,TimeUnit.SECONDS).build(); wm.enqueueUniquePeriodicWork(PERIODIC,ExistingPeriodicWorkPolicy.UPDATE,req) } }
    fun manual(context:Context) { val req=OneTimeWorkRequestBuilder<SyncWorker>().setConstraints(constraints()).setBackoffCriteria(BackoffPolicy.EXPONENTIAL,30,TimeUnit.SECONDS).build(); WorkManager.getInstance(context).enqueueUniqueWork(MANUAL,ExistingWorkPolicy.KEEP,req) }
}

class SyncNotificationManager(private val context:Context) {
    init { (context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager).createNotificationChannel(NotificationChannel("sync","Workout synchronization",NotificationManager.IMPORTANCE_DEFAULT)) }
    fun summary(s:SyncSummary) { if(s.uploaded==0&&s.temporary==0&&s.permanent==0)return; notify(if(s.uploaded>0)"Тренировки синхронизированы" else "Не удалось отправить тренировку",s.text) }
    fun error(message:String)=notify("Синхронизация требует внимания",message)
    private fun notify(title:String,text:String) { (context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager).notify(100,NotificationCompat.Builder(context,"sync").setSmallIcon(android.R.drawable.stat_notify_sync).setContentTitle(title).setContentText(text).setAutoCancel(true).build()) }
}
