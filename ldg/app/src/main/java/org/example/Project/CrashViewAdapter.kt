package org.example.Project

import android.annotation.SuppressLint
import android.app.AlertDialog
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Environment
import android.provider.MediaStore
import android.text.method.LinkMovementMethod
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Filter
import android.widget.Filterable
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat.startActivity
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.example.Project.VideoViewApi
import org.json.JSONObject
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.converter.scalars.ScalarsConverterFactory
import retrofit2.http.GET
import retrofit2.http.Url
import java.io.IOException
import java.net.URL
import java.util.*
import kotlin.collections.ArrayList


class CrashViewAdapter(var crashLists: ArrayList<CrashDataEntity>, var con: Context) :
    RecyclerView.Adapter<CrashViewAdapter.ViewHolder>(), Filterable {
    var TAG = "CrashViewAdapter"

    var filteredcrashLists = ArrayList<CrashDataEntity>()
    var itemFilter = ItemFilter()

    inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {

        var tv_id: TextView
        var tv_videodate: TextView


        init {
            tv_id = itemView.findViewById(R.id.txt_id)
            tv_videodate = itemView.findViewById(R.id.txt_videodate)

            itemView.setOnClickListener {
                AlertDialog.Builder(con).apply {
                    val position = adapterPosition
                    val crashlist = filteredcrashLists[position]
                    setTitle("번호: ${crashlist.ID}")
                    setMessage("제목: ${crashlist.videodate}")
                    setPositiveButton("OK") { dialog, which ->
                        Toast.makeText(con, "OK Button Click", Toast.LENGTH_SHORT).show()
                        saveVideoToGallery(crashlist.videodate)
                    }
                    show()
                }
            }
        }

        private fun saveVideoToGallery(videoUrl: String) {
            GlobalScope.launch {
                try {
                    val baseUrl = CrashViewApi.DOMAIN
                    val apiUrl = "/crashvideo/download/$videoUrl"
                    val downloadUrl = "${baseUrl.trimEnd('/')}$apiUrl"

                    val request = Request.Builder()
                        .url(downloadUrl)
                        .build()

                    val response = OkHttpClient().newCall(request).execute()

                    if (response.isSuccessful) {
                        val crashData = response.body?.byteStream()
                        val crashlist = filteredcrashLists[adapterPosition]
                        val fileName = crashlist.videodate
                        val resolver = con.contentResolver
                        val contentValues = ContentValues().apply {
                            put(MediaStore.Video.Media.DISPLAY_NAME, fileName)
                            put(MediaStore.Video.Media.MIME_TYPE, "video/mp4")
                            put(
                                MediaStore.Video.Media.RELATIVE_PATH,
                                "${Environment.DIRECTORY_PICTURES}/project_crash_video"
                            )
                        }
                        val uri = resolver.insert(
                            MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
                            contentValues
                        )
                        uri?.let {
                            resolver.openOutputStream(it)?.use { outputStream ->
                                crashData?.let { inputStream ->
                                    inputStream.copyTo(outputStream)
                                }
                            }
                        }

                        con.runOnUiThread {
                            Log.i("API_CALL", "$fileName downloaded and saved to gallery")
                            Toast.makeText(con, "$fileName 다운로드 완료", Toast.LENGTH_SHORT).show()
                        }
                    }

                } catch (e: Exception) {

                }
            }
        }
    }
    interface Api {
        @GET
        fun getcrashList(): Call<List<CrashDataEntity>>

        @GET
        fun getVideoUrl(@Url videoUrl: String): Call<String>
    }
    init {
        filteredcrashLists.addAll(crashLists)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val con = parent.context
        val inflater = con.getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
        val view = inflater.inflate(R.layout.crash_item, parent, false)

        return ViewHolder(view)
    }
    override fun getItemCount(): Int {
        return filteredcrashLists.size
    }
    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val crashList: CrashDataEntity = filteredcrashLists[position]
        holder.tv_id.text= "번호 : ${crashList.ID.toString()}"
        holder.tv_videodate.text = "제목 : ${crashList.videodate}"

        // 모든 데이터를 조회하는 경우
        if (position == filteredcrashLists.size - 1) {
            // crashLists를 모두 조회했을 때의 동작을 여기에 구현합니다.
            // 예를 들어, Toast 메시지를 출력하거나 다른 작업을 수행할 수 있습니다.
        }

    }
    fun setList(crashLists: ArrayList<CrashDataEntity>) {
        filteredcrashLists.clear()
        filteredcrashLists.addAll(crashLists)
        this.crashLists = filteredcrashLists
        notifyDataSetChanged()
    }
    fun filter(searchText: String) {
        if (searchText.isNullOrEmpty()) {
            filteredcrashLists.clear()
            filteredcrashLists.addAll(crashLists)
            getDataFromServer()
        } else {
            // 검색어가 있으면 검색어를 포함하는 데이터만 필터링합니다.
            val filteredList = filteredcrashLists.filter { CrashData ->
                CrashData.videodate.contains(searchText)
            }
            filteredcrashLists.clear()
            filteredcrashLists.addAll(filteredList)
            notifyDataSetChanged()
        }
    }
    private fun getDataFromServer() {
        val retrofit = Retrofit.Builder()
            .baseUrl(VideoViewApi.DOMAIN)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val apiService = retrofit.create(CrashService::class.java)
        apiService?.requsetData()?.enqueue(object : Callback<List<CrashDataEntity>> {
            override fun onResponse(call: Call<List<CrashDataEntity>>, response: Response<List<CrashDataEntity>>) {
                if (response.isSuccessful) {
                    crashLists.clear()
                    crashLists.addAll(response.body()!!)
                    filteredcrashLists.clear()
                    filteredcrashLists.addAll(crashLists)
                    notifyDataSetChanged()
                }
            }

            override fun onFailure(call: Call<List<CrashDataEntity>>, t: Throwable) {
                Log.e(TAG, "응답 실패 : ${t.message}")
            }
        })
    }

    //-- filter
    override fun getFilter(): Filter {
        return itemFilter
    }
    fun submitList(dataList: List<CrashDataEntity>) {
        this.crashLists.clear()
        this.crashLists.addAll(dataList) // 전체 데이터를 저장합니다
        this.filteredcrashLists.clear()
        this.filteredcrashLists.addAll(dataList) // 필터링된 데이터를 저장합니다
        notifyDataSetChanged() // 데이터 변경을 recyclerView에 알려줍니다
    }

    inner class ItemFilter : Filter() {
        private var previousFilterString = ""
        override fun performFiltering(charSequence: CharSequence): FilterResults {
            val filterString = charSequence.toString()
            val results = FilterResults()

            if (filterString.isBlank()) {
                // 검색어가 비어있을 경우 전체 데이터 다시 요청
                getDataFromServer()

                results.values = crashLists
                results.count = crashLists.size
                return results
            }

            val filteredList = crashLists.filter { it.videodate.contains(filterString, ignoreCase = true) }
            results.values = filteredList
            results.count = filteredList.size
            return results
        }
        @SuppressLint("NotifyDataSetChanged")
        override fun publishResults(charSequence: CharSequence?, filterResults: FilterResults) {
            val filterString = charSequence.toString().trim()

            if (filterString == null || filterString.isBlank()) {
                // 검색어가 비어있을 경우 전체 데이터 다시 요청
                submitList(crashLists)
            } else {
                val filteredList = filterResults.values as List<CrashDataEntity>
                filteredcrashLists.clear()
                filteredcrashLists.addAll(filteredList)
                if (filterString.contains(previousFilterString)) {
                    // 새로운 검색어가 이전 검색어를 포함할 경우,
                    // 필터링된 데이터가 기존 필터링된 데이터의 부분집합이므로, 이전 결과를 유지한 채로 업데이트합니다.
                    notifyItemRangeChanged(0, filteredList.size)
                } else {
                    // 이전 검색어와 상관없이 전체 데이터가 갱신되어야 하는 경우,
                    // 전체 데이터를 업데이트합니다.
                    submitList(filteredList)
                }
            }
        }

    }
}

