from flask import Flask, request, jsonify, render_template
import os
import VideoDef
import time
import requests

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "videos"
crash_url_video = "http://43.201.154.195:5000/crashvideo/upload"
crash_video_dir = "ShockVideos"


# "/"와 "/upload"를 합쳐서 버튼없이 웹서버 접속시 자동으로 보내게 완성
@app.route("/")
@app.route("/crash", methods=["POST", "GET"])
def upload_video():
    # os.chdir("psw")

    pastvideo = VideoDef.past_video_list(crash_video_dir)

    while True:
        newvideo = VideoDef.new_video_list(crash_video_dir, pastvideo)

        VideoDef.crash_different_video_list(newvideo, pastvideo, crash_url_video)

    # Return a response
    return jsonify({"message": "Videos uploaded successfully."})


if __name__ == "__main__":
    app.run(debug=True)
