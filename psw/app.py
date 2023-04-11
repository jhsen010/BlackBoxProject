from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)


@app.route("/", methods=["POST"])
def send_data():
    render_template("index.html")
    url = "http://example.com/upload"
    video_dir = "/path/to/videos"
    video_files = [
        os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".mp4")
    ]

    for video_file in video_files:
        file_name = os.path.basename(video_file)
        video = {"file": open(video_file, "rb")}
        response = requests.post(url, files=video)
        print(f"{file_name} uploaded. Server response: {response.text}")

    return "Data has been sent!"
