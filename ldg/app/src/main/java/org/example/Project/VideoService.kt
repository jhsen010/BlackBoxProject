package org.example.Project

import retrofit2.Call
import retrofit2.http.GET



class VideoViewApi {
    companion object {

        const val DOMAIN = "http://43.201.154.195:5000"

    }
}

interface VideoService {
    @GET("/normalvideo/select")
    fun requestData() : Call<List<VideoDataEntity>>
}
