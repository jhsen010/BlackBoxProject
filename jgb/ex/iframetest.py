from flask import Flask, render_template

app = Flask(__name__, static_folder="/home/ubuntu/videostreaming/")


@app.route("/")
def index():
    # 로컬 동영상 경로 설정
    video_path = "streamingvideo.mp4"

    # iFrame으로 동영상 재생
    return render_template("iframe.html", video_path=video_path)


if __name__ == "__main__":
    app.run()
