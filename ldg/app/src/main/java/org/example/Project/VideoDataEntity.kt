package org.example.Project

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.google.gson.annotations.SerializedName

// 데이터 베이스의 테이블 행 역할.
// 반드시 PrimaryKey가 있어야 함. (자동 생성은 autoGenerate = true 속성 추가)
// 기본적으로 클래스 이름이 테이블명이지만 따로 지정은 @Entity(tableName = " ")을 사용.
@Entity(tableName = "VideoDataEntity")
data class VideoDataEntity (
    @PrimaryKey
    @SerializedName("ID")
    var ID: Int,
    @SerializedName("videodate")
    var videodate: String
)