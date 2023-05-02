from flask import Flask, request, jsonify, render_template
import os
import VideoDef
import time
import requests

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "videos"
url_video = "http://43.201.154.195:5000/normalvideo/upload"
video_dir = "videos"

app.config["CRASH_FOLDER"] = "ShockVideos"
crash_url_video = "http://43.201.154.195:5000/crashvideo/upload"
crash_video_dir = "ShockVideos"


# "/"와 "/upload"를 합쳐서 버튼없이 웹서버 접속시 자동으로 보내게 완성
@app.route("/")
@app.route("/upload", methods=["POST", "GET"])
def upload_video():
    os.chdir("psw")

    pastvideo = VideoDef.past_video_list(video_dir)

    while True:
        newvideo = VideoDef.new_video_list(video_dir, pastvideo)

        VideoDef.different_video_list(newvideo, pastvideo, url_video)

    # Return a response
    return jsonify({"message": "Videos uploaded successfully."})
    # return render_template("index.html")


@app.route("/crashupload", methods=["POST"])
def upload_crash_video():
    os.chdir("psw")
    # 이전에 보낸 비디오 파일 목록 가져오기
    prev_video_files = [
        os.path.join(crash_video_dir, f)
        for f in os.listdir(crash_video_dir)
        if f.endswith(".mp4")
    ]

    while True:
        # 전송하기전 5분간 기다림
        # time.sleep(300)

        # 새 비디오 파일 목록 가져오기
        new_video_files = [
            os.path.join(crash_video_dir, f)
            for f in os.listdir(crash_video_dir)
            if f.endswith(".mp4") and f not in prev_video_files
        ]

        # 중복되지 않은 비디오 파일만 업로드
        for video_file in new_video_files:
            file_name = os.path.basename(video_file)
            video = {"crashvideo": open(video_file, "rb")}
            response = requests.post(crash_url_video, files=video)
            print(f"{file_name} uploaded. Server response: {response.text}")

            # 업로드한 비디오 파일을 이전에 업로드한 비디오 파일 목록에 추가
            prev_video_files.append(file_name)

    # Return a response
    return jsonify({"message": "Videos uploaded successfully."})


if __name__ == "__main__":
    app.run()
