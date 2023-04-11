from flask import Flask, render_template, request
import requests
import os

os.chdir("/home/pi/2team/psw")

app = Flask(__name__, template_folder="./templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/send", methods=["POST"])
def send_data():
    url = "http://43.201.154.195:5000/sensor/select"
    video_dir = "videos"
    video_files = [
        os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".mp4")
    ]

    for video_file in video_files:
        file_name = os.path.basename(video_file)
        video = {"file": open(video_file, "rb")}
        response = requests.post(url, files=video)
    return "Data has been sent!"


@app.route("/favicon.ico")
def favicon():
    return ""


import logging

logging.basicConfig(filename="app.log", level=logging.DEBUG)

if __name__ == "__main__":
    app.run()
