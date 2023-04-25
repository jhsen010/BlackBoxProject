from flask import Flask, request, jsonify, render_template
import os
import time
import requests

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "ShockVideos"

url_video = "http://43.201.154.195:5000/crashvideo/upload"
video_dir = "ShockVideos"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_video():
    os.chdir("psw")
    # Get a list of previously sent video files
    prev_video_files = [
        os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".mp4")
    ]
    prev_video_file = ""

    while True:
        # wait 5 minutes before sending
        # time.sleep(300)

        # Get a list of new video files
        new_video_files = [
            os.path.join(video_dir, f)
            for f in os.listdir(video_dir)
            if f.endswith(".mp4") and f not in prev_video_files
        ]

        # Sort new video files by name
        new_video_files.sort()

        # Upload only one non-duplicate video file
        if new_video_files:
            video_file = new_video_files[0]
            file_name = os.path.basename(video_file)

            if prev_video_file:
                # Upload the previous video file
                prev_video = {"prev_video": open(prev_video_file, "rb")}
                response = requests.post(url_video, files=prev_video)
                print(f"{prev_video_file} uploaded. Server response: {response.text}")

            # Upload the current video file
            video = {"normalvideo": open(video_file, "rb")}
            response = requests.post(url_video, files=video)
            print(f"{file_name} uploaded. Server response: {response.text}")

            # Update the previous video file
            prev_video_file = video_file

            # Remove the uploaded video file from the list of previously uploaded video files
            prev_video_files.pop(0)

            # Add the current video file to the list of previously uploaded video files
            prev_video_files.append(video_file)

    # Return a response
    return jsonify({"message": "Videos uploaded successfully."})


if __name__ == "__main__":
    app.run()
