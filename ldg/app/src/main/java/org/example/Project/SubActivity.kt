package org.example.Project


import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.SearchView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.*
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory


class SubActivity : AppCompatActivity() {
    var TAG = "SubActivity"
    lateinit var log_list_view: RecyclerView
    lateinit var viewAdapter: ViewAdapter
    lateinit var logLists: ArrayList<LogDataEntity>
    lateinit var searchView: SearchView


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_sub)

        val btn2: Button = findViewById(R.id.btn2)
        val btn3: Button = findViewById(R.id.btn3)

        btn2.setOnClickListener{
            val intent = Intent(this, SubActivity2::class.java)
            startActivity(intent)
        }
        btn3.setOnClickListener{
            val intent = Intent(this, SubActivity3::class.java)
            startActivity(intent)
        }


        log_list_view = findViewById(R.id.log_list_view)



        searchView = findViewById(R.id.search_view)
        searchView = setOnQueryTextListener(searchViewTextListener)

        // videoLists 초기화
        logLists = ArrayList()
        setAdapter()

        val recyclerView: RecyclerView = findViewById(R.id.log_list_view)

        recyclerView.adapter = viewAdapter

        val layoutManager = LinearLayoutManager(baseContext)
        recyclerView.layoutManager = layoutManager

        runOnUiThread {
            viewAdapter.setList(logLists)
            viewAdapter.notifyDataSetChanged()
        }
        GlobalScope.launch(Dispatchers.Main) { // UI 스레드에서 실행
            viewAdapter.setList(logLists)
            viewAdapter.notifyDataSetChanged()
        }
        // 기존에 저장된 데이터를 먼저 RecyclerView에 표시
        GlobalScope.launch {
            val db = AppDatabase.getInstance(applicationContext)
            val logDataEntities = db.LogDataEntityDao().getAll()
            val logDataList = logDataEntities.map {
                LogDataEntity(
                    it.ID,
                    it.date,
                    it.accel,
                    it.strbreak,
                    it.speed
                )
            }
            logLists.clear()
            logLists.addAll(logDataList)
            originalDataList = logDataList
            viewAdapter.setList(logLists)
            viewAdapter.notifyDataSetChanged()
        }

        // API에서 새로운 데이터를 가져와서 Room에 저장하고 RecyclerView에 표시
        getViewApi()
    }


    private fun setOnQueryTextListener(searchViewTextListener: SearchView.OnQueryTextListener): SearchView {
        searchView.setOnQueryTextListener(searchViewTextListener)
        return searchView
    }


    private var isSearchEmpty = true // 초기에 검색어가 비어있다고 가정
    private var originalDataList: List<LogDataEntity> = emptyList() // 전체 데이터를 저장하는 변수

    private var searchViewTextListener: SearchView.OnQueryTextListener =
        object : SearchView.OnQueryTextListener {
            override fun onQueryTextSubmit(query: String?): Boolean {
                return false
            }

            private fun setDataList(list: List<LogDataEntity>) {
                logLists.clear()
                logLists.addAll(list)
                viewAdapter.setList(logLists)
                viewAdapter.notifyDataSetChanged()
            }

            override fun onQueryTextChange(s: String?): Boolean {
                if (s.isNullOrBlank()) {
                    isSearchEmpty = true
                    getViewApi()
                    setDataList(originalDataList)
                } else {
                    isSearchEmpty = false
                    val filteredList = originalDataList.filter { data: LogDataEntity ->
                        data.date.contains(s, true) || data.ID.toString()
                            .contains(s, true) || data.accel.contains(
                            s,
                            true
                        ) || data.speed.toString().contains(s, true) ||
                                data.strbreak.contains(s, true)
                        // 대소문자 구분 없이 검색어가 포함된 데이터만 필터링합니다
                    }
                    val matchingList = originalDataList.filter { data: LogDataEntity ->
                        data.date.contains(s, true) || s.contains(data.date, true)
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
                    viewAdapter.filter.filter(s)
                }
                Log.d(TAG, "Services Text is changed: $s")
                return false
            }
        }

    fun setAdapter() {
        log_list_view.layoutManager = LinearLayoutManager(this)
        viewAdapter = ViewAdapter(logLists, this)
        log_list_view.adapter = viewAdapter
    }
    private suspend fun updateLogs(logs: List<LogDataEntity>) {
        withContext(Dispatchers.IO) {
            val db = AppDatabase.getInstance(applicationContext)
            db.LogDataEntityDao().deleteAll() // 기존 데이터 삭제
            db.LogDataEntityDao().insertAll(logs) // 새로운 데이터 저장
            val newLogDataEntities = db.LogDataEntityDao().getAll() // 새로운 데이터 로드
            val newLogDataList = newLogDataEntities.map { LogDataEntity(it.ID, it.date, it.accel,it.strbreak,it.speed) }
            withContext(Dispatchers.Main) {
                logLists.clear()
                logLists.addAll(newLogDataList)
                originalDataList = newLogDataList
                viewAdapter.setList(logLists)
                viewAdapter.notifyDataSetChanged()
            }
        }
    }

    private fun getViewApi() {
        val retrofit = Retrofit.Builder()
            .baseUrl(ViewApi.DOMAIN)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        val ViewService = retrofit.create(ViewService::class.java)
        ViewService.requestData().enqueue(object : Callback<List<LogDataEntity>> {
            override fun onResponse(
                call: Call<List<LogDataEntity>>,
                response: Response<List<LogDataEntity>>
            ) {
                if (response.isSuccessful) {
                    val logs = response.body()
                    if (logs != null) {
                        MainScope().launch {
                            updateLogs(logs)
                        }
                    }
                } else {
                    Log.e(TAG, "Failed to fetch logs")
                }
            }

            override fun onFailure(call: Call<List<LogDataEntity>>, t: Throwable) {
                Log.e(TAG, "Failed to fetch logs", t)
            }
        })
    }


    fun <E> ArrayList<E>.addAll(elements: List<LogDataEntity>) {
        for (element in elements) {
            this.add(element as E)
        }
    }
}

