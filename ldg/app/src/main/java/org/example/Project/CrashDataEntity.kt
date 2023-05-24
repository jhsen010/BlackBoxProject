package org.example.Project

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.google.gson.annotations.SerializedName

@Entity(tableName = "CrashDataEntity")
data class CrashDataEntity (
    @PrimaryKey
    @SerializedName("ID")
    var ID: Int,
    @SerializedName("videodate")
    var videodate: String
)