package org.example.Project

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.widget.Button
import android.widget.MediaController
import android.widget.VideoView
import androidx.appcompat.app.AppCompatActivity
import org.example.Project.R

@Suppress("DEPRECATION")
class SubActivity4 : AppCompatActivity() {
    private val GALLERY_REQUEST_CODE = 1001
    private lateinit var vv: VideoView
    private lateinit var galleryButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_sub4)

        // VideoView 초기화
        vv = findViewById(R.id.vv)
        vv.setMediaController(MediaController(this))

        // 갤러리 열기 버튼 초기화
        galleryButton = findViewById(R.id.gallery_button)

        // 갤러리 열기 버튼 클릭 시
        galleryButton.setOnClickListener {
            openGallery()
        }
        val btn1:Button = findViewById(R.id.main)
        btn1.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }
    }

    private fun openGallery() {
        val galleryIntent = Intent(Intent.ACTION_PICK, MediaStore.Video.Media.EXTERNAL_CONTENT_URI)
        startActivityForResult(galleryIntent, GALLERY_REQUEST_CODE)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        if (resultCode == RESULT_OK && requestCode == GALLERY_REQUEST_CODE && data != null) {
            // 선택한 비디오의 URI 얻어오기
            val selectedVideoUri: Uri = data.data ?: return

            // VideoView가 보여줄 동영상의 경로 주소(Uri) 설정하기
            vv.setVideoURI(selectedVideoUri)

            // 동영상을 읽어오는데 시간이 걸리므로..
            // 비디오 로딩 준비가 끝났을 때 실행하도록..
            // 리스너 설정
            vv.setOnPreparedListener {
                // 비디오 시작
                vv.start()
            }
        }
    }

    //화면에 안보일 때, 앱이 백그라운드로 들어갈 때
    override fun onPause() {
        super.onPause()

        //비디오 일시 정지
        vv.apply {
            if (isPlaying) pause()
        }
    }

    //액티비티가 메모리에서 사라질 때..
    override fun onDestroy() {
        super.onDestroy()

        // 비디오 정지
        vv.stopPlayback()
    }
}
