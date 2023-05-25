package org.example.Project

import androidx.room.*

@Dao
interface LogDataDao {
    @Query("SELECT * FROM LogDataEntity")
    fun getAll(): List<LogDataEntity>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun insertAll(logDataList: List<LogDataEntity>)

    @Query("DELETE FROM LogDataEntity")
    fun deleteAll()

    @Query("SELECT * FROM LogDataEntity WHERE date LIKE :searchText OR ID LIKE :searchText OR accel LIKE :searchText OR speed LIKE :searchText OR strbreak LIKE :searchText")
    fun searchLogData(searchText: String): List<LogDataEntity>


}