package org.example.Project

import android.content.Context
import androidx.room.*
import org.example.Project.VideoDataDao
import org.example.Project.VideoDataEntity

@Database(entities = [VideoDataEntity::class], version = 1)
abstract class AppDatabase2 : RoomDatabase() {
    abstract fun VideoDataEntityDao(): VideoDataDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase2? = null

        fun getInstance(context: Context): AppDatabase2 {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase2::class.java,
                    "AppDatabase2"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}