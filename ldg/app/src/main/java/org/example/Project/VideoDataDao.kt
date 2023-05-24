package org.example.Project

import androidx.room.*

@Dao
interface VideoDataDao {
    @Query("SELECT * FROM VideoDataEntity")
    fun getAll(): List<VideoDataEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun insertAll(videoDataList: List<VideoDataEntity>)

    @Query("DELETE FROM VideoDataEntity")
    fun deleteAll()

    @Query("SELECT * FROM VideoDataEntity WHERE videodate LIKE :searchText OR ID")
    fun searchLogData(searchText: String): List<VideoDataEntity>

}