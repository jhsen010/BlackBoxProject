package org.example.Project

import retrofit2.Call
import retrofit2.http.GET

class CrashViewApi {
    companion object {

        const val DOMAIN = "http://43.201.154.195:5000"

    }
}
interface CrashService {
    @GET("/crashvideo/select")
    fun requsetData(): Call<List<CrashDataEntity>>

}