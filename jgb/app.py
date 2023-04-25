from flask import Flask, request, jsonify, Response
from flask import stream_with_context, render_template
from dotenv import load_dotenv
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import
import mysql.connector
import boto3
import os


projectlocal = os.path.dirname(__file__)

app = Flask(__name__, static_folder=projectlocal + "/videostreaming/")
api = Api(app)  # Flask 객체에 Api 객체 등록

load_dotenv()
# RDS endpoint, username, password, database name 설정
ENDPOINT = os.environ.get("endpoint")
PORT = os.environ.get("port")
USR = os.environ.get("usr")
PWD = os.environ.get("pwd")
DBNAME = os.environ.get("dbname")

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

strlocal = projectlocal + "/videostreaming/streamingvideo.mp4"


def gen(strlocal):
    with open(strlocal, "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            yield data


@app.route("/videowatch")
def index():
    # 로컬 동영상 경로 설정
    video_path = "streamingvideo.mp4"
    print(video_path)
    # iFrame으로 동영상 재생
    return render_template("iframe.html", video_path=video_path)


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


@api.route("/normalvideo/watch/<strvideodate>")
class watchnormal(Resource):
    def get(self, strvideodate):
        try:
            # data = request.get_json()
            # strvideodate = data["strvideodate"]
            # strvideodate = request.form.get("strvideodate")
            # if strvideodate is None:
            #     return "input data : None "
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

        if not os.path.exists(projectlocal + "/videostreaming"):  # 없으면 만들어
            os.makedirs(projectlocal + "/videostreaming")
        folder_path = projectlocal + "/videostreaming"  # 비우고 싶은 폴더 경로

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)  # 파일 삭제

        s3r.Bucket("mobles3").download_file(
            "normalvideo/" + strvideodate,
            strlocal,
        )

        return "http://43.201.154.195:5000/videowatch"


@api.route("/crashvideo/watch/<strvideodate>")
class watchcrash(Resource):
    def get(self, strvideodate):
        try:
            # data = request.get_json()
            # strvideodate = data["strvideodate"]
            # strvideodate = request.form.get("strvideodate")
            # if strvideodate is None:
            #     return "input data : None "
            print(strvideodate)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ID, videodate FROM camera_crash WHERE videodate = '%s'"
                % strvideodate
            )
            bufferclean = cursor.fetchall()

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video at MySQL table: {error}")
            return f"Failed to find video at MySQL table: {error}"

        if not os.path.exists(projectlocal + "/videostreaming"):  # 없으면 만들어
            os.makedirs(projectlocal + "/videostreaming")
        folder_path = projectlocal + "/videostreaming"  # 비우고 싶은 폴더 경로

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

            if not os.path.exists(projectlocal + "/videoupload"):  # 없으면 만들어
                os.makedirs(projectlocal + "/videoupload")
            file.save(projectlocal + "/videoupload/" + file.filename)

            # 파일 ec2에서 s3로 업로드하기
            local_file = projectlocal + "/videoupload/" + file.filename
            obj_file = "normalvideo/" + file.filename  # S3 에 올라갈 파일명
            bucket.upload_file(local_file, obj_file)

            file_path = projectlocal + "/videoupload/" + file.filename
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

            if not os.path.exists(projectlocal + "/videoupload"):  # 없으면 만들어
                os.makedirs(projectlocal + "/videoupload")
            file.save(projectlocal + "/videoupload/" + file.filename)

            # 파일 ec2에서 s3로 업로드하기
            local_file = projectlocal + "/videoupload/" + file.filename
            obj_file = "crashvideo/" + file.filename  # S3 에 올라갈 파일명
            bucket.upload_file(local_file, obj_file)

            file_path = projectlocal + "/videoupload/" + file.filename
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

            # # 파일 업로드 성공시 메시지 반환
            return jsonify({"message": "File upload success"})

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to video upload: {error}")
            return f"Failed to video upload: {error}"


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
