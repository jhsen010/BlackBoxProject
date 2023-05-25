package org.example.Project

import android.annotation.SuppressLint
import android.app.AlertDialog
import android.content.Context
import android.content.DialogInterface
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.recyclerview.widget.RecyclerView
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory


class ViewAdapter(var logLists: ArrayList<LogDataEntity>, var con: Context) :
    RecyclerView.Adapter<ViewAdapter.ViewHolder>(), Filterable {
    var TAG = "ViewAdapter"

    var filteredlogLists = ArrayList<LogDataEntity>()
    var itemFilter = ItemFilter()
    inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {

        var tv_id: TextView
        var tv_date: TextView
        var tv_accel: TextView
        var tv_strbreak: TextView
        var tv_speed: TextView


        init {
            tv_id = itemView.findViewById(R.id.txt_id)
            tv_date = itemView.findViewById(R.id.txt_date)
            tv_accel = itemView.findViewById(R.id.txt_accel)
            tv_strbreak = itemView.findViewById(R.id.txt_strbreak)
            tv_speed = itemView.findViewById(R.id.txt_speed)

            itemView.setOnClickListener {
                AlertDialog.Builder(con).apply {
                    var position = adapterPosition
                    var loglist = filteredlogLists[position]
                    setTitle("번호 : ${loglist.ID}")
                    setMessage("날짜 : ${loglist.date}\n" + "엑셀 : ${loglist.accel}\n" + "브레이크 : ${loglist.strbreak}\n" + "속도 : ${loglist.speed}")
                    setPositiveButton("OK", DialogInterface.OnClickListener { dialog, which ->
                        Toast.makeText(con, "OK Button Click", Toast.LENGTH_SHORT).show()
                    })
                    show()
                }
            }
        }
    }

    init {
        filteredlogLists.addAll(logLists)
    }


    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val con = parent.context
        val inflater = con.getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
        val view = inflater.inflate(R.layout.log_item, parent, false)

        return ViewHolder(view)
    }
    private var itemCount: Int = 0
    override fun getItemCount(): Int {
        return filteredlogLists.size
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val logList: LogDataEntity = filteredlogLists[position]
        holder.tv_id.text = "번호 : ${logList.ID.toString()}"
        holder.tv_date.text = "날짜 : ${logList.date}"
        holder.tv_accel.text = "엑셀 : ${logList.accel}"
        holder.tv_strbreak.text = "브레이크 : ${logList.strbreak}"
        holder.tv_speed.text = "속도 : ${logList.speed.toString()}"
        // 모든 데이터를 조회하는 경우
        if (position == filteredlogLists.size - 1) {
            // logList를 모두 조회했을 때의 동작을 여기에 구현합니다.
            // 예를 들어, Toast 메시지를 출력하거나 다른 작업을 수행할 수 있습니다.
        }
    }

    fun setList(videoLists: ArrayList<LogDataEntity>) {
        filteredlogLists.clear()
        filteredlogLists.addAll(videoLists)
        this.logLists = filteredlogLists
        notifyDataSetChanged()
    }

    // filter 메소드 수정
    fun filter(searchText: String?) {
        if (searchText.isNullOrEmpty()) {
            // 검색어가 없으면 모든 데이터를 필터링합니다.
            filteredlogLists.clear()
            filteredlogLists.addAll(logLists)
            getDataFromServer()
        } else {
            // 검색어가 있으면 검색어를 포함하는 데이터만 필터링합니다.
            val filteredList = logLists.filter { logData ->
                logData.date.contains(searchText, true)
            }
            filteredlogLists.clear()
            filteredlogLists.addAll(filteredList)
            notifyDataSetChanged()
        }
    }


    //-- filter
    override fun getFilter(): Filter {
        return itemFilter
    }


    fun submitList(dataList: List<LogDataEntity>) {
        this.logLists.clear()
        this.logLists.addAll(dataList) // 전체 데이터를 저장합니다
        this.filteredlogLists.clear()
        this.filteredlogLists.addAll(dataList) // 필터링된 데이터를 저장합니다
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

                results.values = logLists
                results.count = logLists.size
                previousFilterString = ""
                return results
            }

            val filteredList = logLists.filter { it.date.contains(filterString, ignoreCase = true) }
            results.values = filteredList
            results.count = filteredList.size
            previousFilterString = filterString
            return results
        }

        @SuppressLint("NotifyDataSetChanged")
        override fun publishResults(charSequence: CharSequence?, filterResults: FilterResults) {
            val filterString = charSequence?.toString()?.trim()

            if (filterString == null || filterString.isBlank()) {
                // 검색어가 없는 경우 전체 데이터를 표시합니다.
                submitList(logLists)
            } else {
                val filteredList = filterResults.values as List<LogDataEntity>
                filteredlogLists.clear()
                filteredlogLists.addAll(filteredList)
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
    private fun getDataFromServer() {
        val retrofit = Retrofit.Builder()
            .baseUrl(ViewApi.DOMAIN)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val apiService = retrofit.create(ViewService::class.java)
        apiService?.requestData()?.enqueue(object : Callback<List<LogDataEntity>> {
            override fun onResponse(call: Call<List<LogDataEntity>>, response: Response<List<LogDataEntity>>) {
                if (response.isSuccessful) {
                    logLists.clear()
                    logLists.addAll(response.body()!!)
                    filteredlogLists.clear()
                    filteredlogLists.addAll(logLists)
                    notifyDataSetChanged()
                }
            }

            override fun onFailure(call: Call<List<LogDataEntity>>, t: Throwable) {
                Log.e(TAG, "응답 실패 : ${t.message}")
            }
        })
    }

}


private fun <E> ArrayList<E>.addAll(elements: ArrayList<LogDataEntity>) {
    for (element in elements) {
        this.add(element as E)
    }
}

