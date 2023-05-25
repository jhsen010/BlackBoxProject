package org.example.Project

import android.content.Context
import androidx.room.*
import org.example.Project.LogDataDao
import org.example.Project.LogDataEntity

@Database(entities = [LogDataEntity::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun LogDataEntityDao(): LogDataDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "AppDatabase"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}