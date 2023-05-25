package org.example.Project



import retrofit2.Call
import retrofit2.http.GET



class ViewApi {
    companion object {

        const val DOMAIN = "http://43.201.154.195:5000"
    }
}
interface ViewService {
    @GET("/sensor/select")
    fun requestData() : Call<List<LogDataEntity>>
}