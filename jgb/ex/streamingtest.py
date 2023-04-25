from flask import Flask, Response

app = Flask(__name__)


def gen():
    with open("/home/ubuntu/videostreaming/test.mp4", "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            yield data


@app.route("/video")
def video_feed():
    return Response(gen(), mimetype="video/mp4")


if __name__ == "__main__":
    app.run(debug=True)
