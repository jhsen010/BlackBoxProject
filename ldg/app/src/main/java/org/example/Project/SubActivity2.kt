package org.example.Project

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.Button

import android.widget.SearchView
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.*
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import org.example.Project.*


class SubActivity2 : AppCompatActivity() {
    var TAG = "SubActivity2"
    lateinit var video_list_view : RecyclerView
    lateinit var videoviewAdapter: VideoViewAdapter
    lateinit var videoLists: ArrayList<VideoDataEntity>
    lateinit var searchView: SearchView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_sub2)

        val btn2: Button = findViewById(R.id.btn2)
        val btn3: Button = findViewById(R.id.btn3)
        val btn4:Button = findViewById(R.id.gallery_button)

        btn2.setOnClickListener{
            val intent = Intent(this, SubActivity::class.java)
            startActivity(intent)
        }
        btn3.setOnClickListener{
            val intent = Intent(this, SubActivity3::class.java)
            startActivity(intent)
        }
        btn4.setOnClickListener{
            val intent = Intent(this, SubActivity4::class.java)
            startActivity(intent)
        }

        video_list_view = findViewById(R.id.video_list_view)


        searchView = findViewById(R.id.search_view)
        searchView = setOnQueryTextListener(searchViewTextListener)

        // videoLists 초기화
        videoLists = ArrayList()
        setAdapter()

        val recyclerView: RecyclerView = findViewById(R.id.video_list_view)
        recyclerView.adapter = videoviewAdapter

        val layoutManager = LinearLayoutManager(baseContext)
        recyclerView.layoutManager = layoutManager

        // 기존에 저장된 데이터를 먼저 RecyclerView에 표시
        GlobalScope.launch {
            val db = AppDatabase2.getInstance(applicationContext)
            val videoDataEntities = db.VideoDataEntityDao().getAll()
            val videoDataList = videoDataEntities.map {VideoDataEntity(it.ID, it.videodate) }
            videoLists.clear()
            videoLists.addAll(videoDataList)
            originalDataList = videoDataList
            videoviewAdapter.setList(videoLists)
            videoviewAdapter.notifyDataSetChanged()
        }

        // API에서 새로운 데이터를 가져와서 Room에 저장하고 RecyclerView에 표시
        getViewApi()
    }
    private fun setOnQueryTextListener(searchViewTextListener: SearchView.OnQueryTextListener): SearchView {
        searchView.setOnQueryTextListener(searchViewTextListener)
        return searchView
    }


    private var isSearchEmpty = true // 초기에 검색어가 비어있다고 가정
    private var originalDataList: List<VideoDataEntity> = emptyList() // 전체 데이터를 저장하는 변수

    private var searchViewTextListener: SearchView.OnQueryTextListener=
        object: SearchView.OnQueryTextListener{
            override fun onQueryTextSubmit(query: String?): Boolean {
                return false
            }

            private fun setDataList(list: List<VideoDataEntity>) {
                videoLists.clear()
                videoLists.addAll(list)
                videoviewAdapter.setList(videoLists)
                videoviewAdapter.notifyDataSetChanged()
            }

            override fun onQueryTextChange(s: String?): Boolean {
                if (s.isNullOrBlank()) {
                    isSearchEmpty = true
                    getViewApi()
                    setDataList(originalDataList)
                } else {
                    isSearchEmpty = false
                    val filteredList = originalDataList.filter { data: VideoDataEntity ->
                        data.videodate.contains(s, true) || data.ID.toString().contains(s,true)
                        // 대소문자 구분 없이 검색어가 포함된 데이터만 필터링합니다
                    }

                    val matchingList = originalDataList.filter { data: VideoDataEntity ->
                        data.videodate.contains(s, true) || s.contains(data.videodate, true)
                        // searchView에 써져있는 텍스트와 일치하는 데이터의 텍스트가 있는지 찾습니다
                        // 검색어가 date 텍스트에 포함되어 있거나, date 텍스트가 검색어에 포함되어 있는 데이터를 모두 찾습니다.
                    }
                    if (matchingList.isNotEmpty()) {
                        setDataList(matchingList) // 일치하는 데이터를 recyclerView에 설정합니다
                    } else {
                        // 필터링된 데이터에서 searchView에 써져 있는 텍스트와 일치하는 데이터의 텍스트가 없을 경우, 첫 번째 데이터를 표시합니다.
                        val firstMatchingData = filteredList.firstOrNull()
                        if (firstMatchingData != null) {
                            setDataList(listOf(firstMatchingData))
                        } else {
                            setDataList(emptyList())
                        }
                    }
                    videoviewAdapter.filter.filter(s)
                }
                Log.d(TAG, "Services Text is changed: $s")
                return false
            }


        }
    fun setAdapter(){
        video_list_view.layoutManager = LinearLayoutManager(this)
        videoviewAdapter = VideoViewAdapter(videoLists,this)
        video_list_view.adapter=videoviewAdapter
    }
    private suspend fun updateVideos(videos: List<VideoDataEntity>) {
        withContext(Dispatchers.IO) {
            val db = AppDatabase2.getInstance(applicationContext)
            db.VideoDataEntityDao().deleteAll() // 기존 데이터 삭제
            db.VideoDataEntityDao().insertAll(videos) // 새로운 데이터 저장
            val newVideoDataEntities = db.VideoDataEntityDao().getAll() // 새로운 데이터 로드
            val newVideoDataList = newVideoDataEntities.map {VideoDataEntity(it.ID, it.videodate) }
            withContext(Dispatchers.Main) {
                videoLists.clear()
                videoLists.addAll(newVideoDataList)
                originalDataList = newVideoDataList
                videoviewAdapter.setList(videoLists)
                videoviewAdapter.notifyDataSetChanged()
            }
        }
    }

    private fun getViewApi() {
        val retrofit = Retrofit.Builder()
            .baseUrl(VideoViewApi.DOMAIN)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        val VideoService = retrofit.create(VideoService::class.java)
        VideoService.requestData().enqueue(object : Callback<List<VideoDataEntity>> {
            override fun onResponse(
                call: Call<List<VideoDataEntity>>,
                response: Response<List<VideoDataEntity>>
            ) {
                if (response.isSuccessful) {
                    val videos = response.body()
                    if (videos != null) {
                        MainScope().launch {
                            updateVideos(videos)
                        }
                    }
                } else {
                    Log.e(TAG, "Failed to fetch videos")
                }
            }

            override fun onFailure(call: Call<List<VideoDataEntity>>, t: Throwable) {
                Log.e(TAG, "Failed to fetch videos", t)
            }
        })
    }


    fun <E> ArrayList<E>.addAll(elements: List<VideoDataEntity>) {
        for (element in elements) {
            this.add(element as E)
        }

    }
}
