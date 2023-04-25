from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def home():
    client_ip = request.environ["REMOTE_ADDR"]
    server_addr = f"http://{client_ip}:5000/"
    return server_addr


if __name__ == "__main__":
    app.run(host="0.0.0.0")
