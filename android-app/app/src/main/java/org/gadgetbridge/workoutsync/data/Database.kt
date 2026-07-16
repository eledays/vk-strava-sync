package org.gadgetbridge.workoutsync.data

import android.content.Context
import androidx.room.*
import kotlinx.coroutines.flow.Flow

enum class SyncStatus { PENDING, UPLOADING, UPLOADED, RETRY_REQUIRED, PERMANENT_ERROR }

@Entity(tableName = "workout_files", indices = [Index(value = ["sha256"], unique = true)])
data class WorkoutFileEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val sha256: String, val uri: String, val fileName: String, val mimeType: String?,
    val sizeBytes: Long?, val modifiedAt: Long?, val discoveredAt: Long,
    val status: SyncStatus = SyncStatus.PENDING, val attempts: Int = 0,
    val lastAttemptAt: Long? = null, val uploadedAt: Long? = null,
    val lastHttpCode: Int? = null, val lastError: String? = null,
)

class Converters {
    @TypeConverter fun fromStatus(value: SyncStatus) = value.name
    @TypeConverter fun toStatus(value: String) = SyncStatus.valueOf(value)
}

@Dao
interface WorkoutFileDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE) suspend fun insert(file: WorkoutFileEntity): Long
    @Query("SELECT * FROM workout_files WHERE sha256=:hash") suspend fun byHash(hash: String): WorkoutFileEntity?
    @Query("SELECT * FROM workout_files WHERE status IN ('PENDING','RETRY_REQUIRED') ORDER BY discoveredAt LIMIT :limit") suspend fun queue(limit: Int = 100): List<WorkoutFileEntity>
    @Query("SELECT * FROM workout_files ORDER BY discoveredAt DESC LIMIT :limit") fun recent(limit: Int = 20): Flow<List<WorkoutFileEntity>>
    @Query("SELECT COUNT(*) FROM workout_files WHERE status IN ('PENDING','RETRY_REQUIRED','UPLOADING')") fun pendingCount(): Flow<Int>
    @Query("SELECT COUNT(*) FROM workout_files WHERE status='UPLOADED'") fun uploadedCount(): Flow<Int>
    @Query("SELECT COUNT(*) FROM workout_files WHERE status='PERMANENT_ERROR'") fun errorCount(): Flow<Int>
    @Query("UPDATE workout_files SET status='RETRY_REQUIRED', lastError='Предыдущая попытка была прервана' WHERE status='UPLOADING'") suspend fun recoverInterrupted()
    @Query("UPDATE workout_files SET status='UPLOADING', attempts=attempts+1, lastAttemptAt=:at, lastError=NULL WHERE id=:id AND status IN ('PENDING','RETRY_REQUIRED')") suspend fun claim(id: Long, at: Long): Int
    @Query("UPDATE workout_files SET status='UPLOADED', uploadedAt=:at, lastHttpCode=:code, lastError=NULL WHERE id=:id") suspend fun success(id: Long, at: Long, code: Int)
    @Query("UPDATE workout_files SET status='RETRY_REQUIRED', lastHttpCode=:code, lastError=:error WHERE id=:id") suspend fun retry(id: Long, code: Int?, error: String)
    @Query("UPDATE workout_files SET status='PERMANENT_ERROR', lastHttpCode=:code, lastError=:error WHERE id=:id") suspend fun permanent(id: Long, code: Int?, error: String)
    @Query("UPDATE workout_files SET status='PENDING', lastError=NULL WHERE id=:id") suspend fun requeue(id: Long)
}

@Database(entities = [WorkoutFileEntity::class], version = 1, exportSchema = false)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun workoutFiles(): WorkoutFileDao
    companion object { fun create(context: Context) = Room.databaseBuilder(context, AppDatabase::class.java, "workouts.db").build() }
}
