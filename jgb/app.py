from flask import (
    Flask,
    request,
    jsonify,
    Response,
    stream_with_context,
    render_template,
)
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import
import mysql.connector
import boto3
import os

app = Flask(__name__, static_folder="/home/ubuntu/videostreaming/")
api = Api(app)  # Flask 객체에 Api 객체 등록

# RDS endpoint, username, password, database name 설정
ENDPOINT = "moble.ckaipdhtuyli.ap-northeast-2.rds.amazonaws.com"
PORT = "3306"
USR = "moble_project"
PWD = "qoawkddj23"
DBNAME = "moble_project"

# RDS에 연결
try:
    conn = mysql.connector.connect(
        host=ENDPOINT, port=PORT, user=USR, password=PWD, database=DBNAME
    )
    print("Connected to RDS successfully!")
except Exception as e:
    print("Unable to connect to RDS.")
    print(e)

s3c = boto3.client("s3")  # 비디오 다운용

s3r = boto3.resource("s3")  # 비디오 업용
bucket_name = "mobles3"
bucket = s3r.Bucket(bucket_name)


def gen(strlocal):
    with open(strlocal, "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            yield data


strlocal = "/home/ubuntu/videostreaming/streamingvideo.mp4"


# @app.route("/videowatch")
# def video_feed():
#     return Response(gen(strlocal), mimetype="video/mp4")


@app.route("/videowatch")
def index():
    # 로컬 동영상 경로 설정
    video_path = "streamingvideo.mp4"

    # iFrame으로 동영상 재생
    return render_template("iframe.html", video_path=video_path)


@api.route("/hello")  # 데코레이터 이용, '/hello' 경로에 클래스 등록
class HelloWorld(Resource):
    def get(self):  # GET 요청시 리턴 값에 해당 하는 dict를 JSON 형태로 반환
        return {"hello": "/sensor/insert or /sensor/select"}


@api.route("/sensor/insert", methods=["POST"])
class sensorinsert(Resource):
    def post(self):
        try:
            data = request.get_json()
            strdate = data["strdate"]
            straccel = data["straccel"]
            strbreak = data["strbreak"]
            intspeed = data["intspeed"]
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sensor (date, accel, break, speed) VALUES ('%s', '%s', '%s', %d)"
                % (strdate, straccel, strbreak, intspeed)
            )
            cursor.execute("ALTER TABLE sensor AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
            cursor.execute("SET @COUNT = 0;")
            cursor.execute("UPDATE sensor SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
            conn.commit()
            return {
                "inserted successfully!": "%s, %s, %s, %d"
                % (strdate, straccel, strbreak, intspeed)
            }
        except Exception as e:
            print("Error inserting record.")
            print(e)
            return "Error inserting record."
        # except mysql.connector.Error as error:  # 원인찾기용도
        #     print(f"Failed to insert record into MySQL table: {error}")
        #     return f"Failed to insert record into MySQL table: {error}"


@api.route("/sensor/select")
class select(Resource):
    def get(self):
        try:
            cursor = conn.cursor()
            cursor.execute("ALTER TABLE sensor AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
            cursor.execute("SET @COUNT = 0;")
            cursor.execute("UPDATE sensor SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
            cursor.execute("SELECT * FROM sensor")
            records = cursor.fetchall()

            data = []
            for row in records:
                obj = {}
                obj["ID"] = row[0]
                obj["date"] = row[1]
                obj["accel"] = row[2]
                obj["break"] = row[3]
                obj["speed"] = row[4]
                data.append(obj)

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to select database of MySQL table: {error}")
            return f"Failed to select database of MySQL table: {error}"


@api.route("/normalvideo/select")
class select(Resource):
    def get(self):
        try:
            cursor = conn.cursor()
            cursor.execute("ALTER TABLE camera_normal AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
            cursor.execute("SET @COUNT = 0;")
            cursor.execute(
                "UPDATE camera_normal SET ID = @COUNT:=@COUNT+1"
            )  # ID순서 꼬인거 풀기
            cursor.execute("SELECT * FROM camera_normal")
            records = cursor.fetchall()

            data = []
            for row in records:
                obj = {}
                obj["ID"] = row[0]
                obj["videodate"] = row[1]
                data.append(obj)

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to select database of MySQL table: {error}")
            return f"Failed to select database of MySQL table: {error}"


@api.route("/crashvideo/select")
class select(Resource):
    def get(self):
        try:
            cursor = conn.cursor()
            cursor.execute("ALTER TABLE camera_crash AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
            cursor.execute("SET @COUNT = 0;")
            cursor.execute(
                "UPDATE camera_crash SET ID = @COUNT:=@COUNT+1"
            )  # ID순서 꼬인거 풀기
            cursor.execute("SELECT * FROM camera_crash")
            records = cursor.fetchall()

            data = []
            for row in records:
                obj = {}
                obj["ID"] = row[0]
                obj["videodate"] = row[1]
                data.append(obj)

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to select database of MySQL table: {error}")
            return f"Failed to select database of MySQL table: {error}"


@api.route("/normalvideo/watch", methods=["POST"])
class watchnormal(Resource):
    def post(self):
        try:
            # data = request.get_json()
            # strvideodate = data["strvideodate"]
            strvideodate = request.form.get("strvideodate")
            print(strvideodate)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ID, videodate FROM camera_normal WHERE videodate = '%s'"
                % strvideodate
            )
            bufferclean = cursor.fetchall()

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video at MySQL table: {error}")
            return f"Failed to find video at MySQL table: {error}"

        folder_path = "/home/ubuntu/videostreaming"  # 비우고 싶은 폴더 경로

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)  # 파일 삭제

        s3r.Bucket("mobles3").download_file(
            "normalvideo/" + strvideodate,
            strlocal,
        )

        return "http://43.201.154.195:5000/videowatch"


@api.route("/crashvideo/watch", methods=["POST"])
class watchcrash(Resource):
    def post(self):
        try:
            data = request.get_json()
            strvideodate = data["strvideodate"]
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ID, videodate FROM camera_crash WHERE videodate = '%s'"
                % strvideodate
            )
            bufferclean = cursor.fetchall()
            print(strvideodate)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video at MySQL table: {error}")
            return f"Failed to find video at MySQL table: {error}"

        folder_path = "/home/ubuntu/videostreaming"  # 비우고 싶은 폴더 경로

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)  # 파일 삭제

        s3r.Bucket("mobles3").download_file(
            "crashvideo/" + strvideodate,
            strlocal,
        )

        return "http://43.201.154.195:5000/videowatch"


@api.route("/normalvideo/upload")
class normalvideo(Resource):
    def post(self):
        try:
            # 업로드된 파일 ec2에 저장
            file = request.files["normalvideo"]  # 'file'은 업로드된 파일의 key 값입니다.

            file.save("/home/ubuntu/videoupload/" + file.filename)
            print(file.filename)

            # 파일 ec2에서 s3로 업로드하기
            local_file = "/home/ubuntu/videoupload/" + file.filename
            obj_file = "normalvideo/" + file.filename  # S3 에 올라갈 파일명
            bucket.upload_file(local_file, obj_file)

            file_path = "/home/ubuntu/videoupload/" + file.filename
            os.remove(file_path)
            print(f"{local_file} uploaded to s3://{bucket_name}/{obj_file}")

            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO camera_normal (videodate) VALUES ('%s')" % file.filename
            )
            cursor.execute("ALTER TABLE camera_normal AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
            cursor.execute("SET @COUNT = 0;")
            cursor.execute(
                "UPDATE camera_normal SET ID = @COUNT:=@COUNT+1"
            )  # ID순서 꼬인거 풀기
            conn.commit()

            # # 파일 업로드 성공시 메시지 반환
            return jsonify({"message": "File upload success"})

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to video upload: {error}")
            return f"Failed to video upload: {error}"


@api.route("/crashvideo/upload")
class crashvideo(Resource):
    def post(self):
        try:
            # 업로드된 파일 ec2에 저장
            file = request.files["crashvideo"]  # 'file'은 업로드된 파일의 key 값입니다.
            file.save("/home/ubuntu/videoupload/" + file.filename)

            # 파일 ec2에서 s3로 업로드하기
            local_file = "/home/ubuntu/videoupload/" + file.filename
            obj_file = "crashvideo/" + file.filename  # S3 에 올라갈 파일명
            bucket.upload_file(local_file, obj_file)

            file_path = "/home/ubuntu/videoupload/" + file.filename
            os.remove(file_path)
            print(f"{local_file} uploaded to s3://{bucket_name}/{obj_file}")

            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO camera_crash (videodate) VALUES ('%s')" % file.filename
            )
            cursor.execute("ALTER TABLE camera_crash AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
            cursor.execute("SET @COUNT = 0;")
            cursor.execute(
                "UPDATE camera_crash SET ID = @COUNT:=@COUNT+1"
            )  # ID순서 꼬인거 풀기
            conn.commit()

            # 파일 업로드 성공시 메시지 반환
            return jsonify({"message": "File upload success"})
        except Exception as e:
            print("file uploading file.")
            print(e)
            return jsonify({"message": "File upload failed"})


@api.route("/normalvideo/download")  # 다운로드는 잠정적으로 사용 안함
class videodown(Resource):
    def generate_presigned_url(self, bucket_name, object_name, expiration=3600):
        response = s3c.generate_presigned_url(
            "get_object",
            Params={"Bucket": "mobles3", "Key": "normalvideo/test.mp4"},
            ExpiresIn=expiration,
        )
        return response

    def get(self):
        url = self.generate_presigned_url(bucket_name, "normalvideo/test.mp4")
        return {"url": url}


@api.route("/normalvideo/find", methods=["POST"])  # 검색기능 만들기만해둠
class selectnormal(Resource):
    def post(self):
        try:
            data = request.get_json()
            strvideodate = data["strvideodate"]
            cursor = conn.cursor()
            findword = "%" + strvideodate + "%"
            cursor.execute(
                "SELECT ID, videodate FROM camera_normal WHERE videodate like  '%s'"
                % findword
            )
            records = cursor.fetchall()

            data = []
            for row in records:
                obj = {}
                obj["ID"] = row[0]
                obj["videodate"] = row[1]
                data.append(obj)

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video of MySQL table: {error}")
            return f"Failed to find video of MySQL table: {error}"


@api.route("/crashvideo/find", methods=["POST"])
class selectnormal(Resource):
    def post(self):
        try:
            data = request.get_json()
            strvideodate = data["strvideodate"]
            cursor = conn.cursor()
            findword = "%" + strvideodate + "%"
            cursor.execute(
                "SELECT ID, videodate FROM camera_crash WHERE videodate like  '%s'"
                % findword
            )
            records = cursor.fetchall()

            data = []
            for row in records:
                obj = {}
                obj["ID"] = row[0]
                obj["videodate"] = row[1]
                data.append(obj)

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video of MySQL table: {error}")
            return f"Failed to find video of MySQL table: {error}"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
