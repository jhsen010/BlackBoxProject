package org.example.Project

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.google.gson.annotations.SerializedName

@Entity(tableName = "LogDataEntity")
data class LogDataEntity(
    @PrimaryKey
    @SerializedName("ID")
    var ID: Int,
    @SerializedName("date")
    var date: String,
    @SerializedName("accel")
    var accel: String,
    @SerializedName("break")
    var strbreak: String,
    @SerializedName("speed")
    var speed: Int,
)
