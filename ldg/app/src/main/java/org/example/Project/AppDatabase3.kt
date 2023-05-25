package org.example.Project

import android.content.Context
import androidx.room.*


@Database(entities = [CrashDataEntity::class], version = 1)
abstract class AppDatabase3 : RoomDatabase() {
    abstract fun CrashDataEntityDao(): CrashDataDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase3? = null

        fun getInstance(context: Context): AppDatabase3 {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase3::class.java,
                    "AppDatabase3"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}