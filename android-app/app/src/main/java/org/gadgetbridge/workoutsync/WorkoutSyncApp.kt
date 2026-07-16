package org.gadgetbridge.workoutsync

import android.app.Application
import org.gadgetbridge.workoutsync.data.*
import org.gadgetbridge.workoutsync.sync.SyncNotificationManager

class WorkoutSyncApp:Application() {
    val db by lazy { AppDatabase.create(this) }
    val settings by lazy { SettingsRepository(this) }
    val scanner by lazy { DocumentTreeScanner(this) }
    val uploader by lazy { UploadClient(contentResolver) }
    val notifications by lazy { SyncNotificationManager(this) }
    override fun onCreate() { super.onCreate(); notifications }
}
