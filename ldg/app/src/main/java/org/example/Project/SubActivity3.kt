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

class SubActivity3 : AppCompatActivity() {
    var TAG = "SubActivity3"
    lateinit var crash_list_view: RecyclerView
    lateinit var crashviewAdapter: CrashViewAdapter
    lateinit var crashLists: ArrayList<CrashDataEntity>
    lateinit var searchView: SearchView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_sub3)

        val btn2: Button = findViewById(R.id.btn2)
        val btn3: Button = findViewById(R.id.btn3)
        val btn4:Button = findViewById(R.id.gallery_button)

        btn2.setOnClickListener {
            val intent = Intent(this, SubActivity::class.java)
            startActivity(intent)
        }

        btn3.setOnClickListener {
            val intent = Intent(this, SubActivity2::class.java)
            startActivity(intent)
        }
        btn4.setOnClickListener{
            val intent = Intent(this, SubActivity4::class.java)
            startActivity(intent)
        }
        crash_list_view = findViewById(R.id.crash_list_view)

        searchView = findViewById(R.id.search_view)
        searchView = setOnQueryTextListener(searchViewTextListener)

        // crashLists 초기화
        crashLists = ArrayList()
        setAdapter()

        val recyclerView: RecyclerView = findViewById(R.id.crash_list_view)
        recyclerView.adapter = crashviewAdapter

        val layoutManager = LinearLayoutManager(baseContext)
        recyclerView.layoutManager = layoutManager

        // 기존에 저장된 데이터를 먼저 RecyclerView에 표시
        GlobalScope.launch {
            val db = AppDatabase3.getInstance(applicationContext)
            val crashDataEntities = db.CrashDataEntityDao().getAll()
            val crashDataList = crashDataEntities.map { CrashDataEntity(it.ID, it.videodate) }
            crashLists.clear()
            crashLists.addAll(crashDataList)
            originalDataList = crashDataList
            crashviewAdapter.setList(crashLists)
            crashviewAdapter.notifyDataSetChanged()
        }

        // API에서 새로운 데이터를 가져와서 Room에 저장하고 RecyclerView에 표시
        getViewApi()
    }

    private fun setOnQueryTextListener(searchViewTextListener: SearchView.OnQueryTextListener): SearchView {
        searchView.setOnQueryTextListener(searchViewTextListener)
        return searchView
    }

    private var isSearchEmpty = true // 초기에 검색어가 비어있다고 가정
    private var originalDataList: List<CrashDataEntity> = emptyList() // 전체 데이터를 저장하는 변수

    private var searchViewTextListener: SearchView.OnQueryTextListener =
        object : SearchView.OnQueryTextListener {
            override fun onQueryTextSubmit(query: String?): Boolean {
                return false
            }

            private fun setDataList(list: List<CrashDataEntity>) {
                crashLists.clear()
                crashLists.addAll(list)
                crashviewAdapter.setList(crashLists)
                crashviewAdapter.notifyDataSetChanged()
            }

            override fun onQueryTextChange(s: String?): Boolean {
                if (s.isNullOrEmpty()) { // 검색어가 비어있으면 전체 데이터를 다시 로드
                    isSearchEmpty = true
                    getViewApi()
                    setDataList(originalDataList)
                } else {
                    isSearchEmpty = false
                    val filteredList = originalDataList.filter { data: CrashDataEntity ->
                        data.videodate.contains(s, true) || data.ID.toString().contains(s, true)
                        // 대소문자 구분 없이 검색어가 포함된 데이터만 필터링합니다
                    }

                    val matchingList = originalDataList.filter { data: CrashDataEntity ->
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
                    crashviewAdapter.filter.filter(s)
                }
                Log.d(TAG, "Services Text is changed: $s")
                return false
            }
        }

    fun setAdapter() {
        crash_list_view.layoutManager = LinearLayoutManager(this)
        crashviewAdapter = CrashViewAdapter(crashLists, this)
        crash_list_view.adapter = crashviewAdapter
    }

    private suspend fun updateCrashVideos(crashs: List<CrashDataEntity>) {
        withContext(Dispatchers.IO) {
            val db = AppDatabase3.getInstance(applicationContext)
            db.CrashDataEntityDao().deleteAll() // 기존 데이터 삭제
            db.CrashDataEntityDao().insertAll(crashs) // 새로운 데이터 저장
            val newCrashDataEntities = db.CrashDataEntityDao().getAll() // 새로운 데이터 로드
            val newCrashDataList = newCrashDataEntities.map { CrashDataEntity(it.ID, it.videodate) }
            withContext(Dispatchers.Main) {
                crashLists.clear()
                crashLists.addAll(newCrashDataList)
                originalDataList = newCrashDataList
                crashviewAdapter.setList(crashLists)
                crashviewAdapter.notifyDataSetChanged()
            }
        }
    }

    private fun getViewApi() {
        val retrofit = Retrofit.Builder()
            .baseUrl(CrashViewApi.DOMAIN)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        val CrashService = retrofit.create(CrashService::class.java)
        CrashService.requsetData().enqueue(object : Callback<List<CrashDataEntity>> {
            override fun onResponse(
                call: Call<List<CrashDataEntity>>,
                response: Response<List<CrashDataEntity>>
            ) {
                if (response.isSuccessful) {
                    val crashs = response.body()
                    if (crashs != null) {
                        MainScope().launch {
                            updateCrashVideos(crashs)
                        }
                    }
                } else {
                    Log.e(TAG, "Failed to fetch crash videos")
                }
            }

            override fun onFailure(call: Call<List<CrashDataEntity>>, t: Throwable) {
                Log.e(TAG, "Failed to fetch crash videos", t)
            }
        })
    }


    fun <E> ArrayList<E>.addAll(elements: List<CrashDataEntity>) {
        for (element in elements) {
            this.add(element as E)
        }
    }
}