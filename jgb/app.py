from flask import Flask, request, jsonify, Response
from flask import stream_with_context, render_template
from dotenv import load_dotenv
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import
import mysql.connector
import boto3
import os
import urllib.request
from flask import send_file
from flask import redirect, url_for

from videocode import video_func
from DBcode import DB_func
from DBcode.DB_func import Database
from videocode.video_func import Videofunc

projectlocal = os.path.dirname(__file__)

app = Flask(__name__, static_folder=projectlocal + "/videostreaming/")
api = Api(app)  # Flask 객체에 Api 객체 등록

DBset = Database()
Videoset = Videofunc()
conn = DBset.rds_connect()  # 이게 된다고?

s3c, s3r, bucket, bucket_name = Videoset.video_init()


@app.route("/videowatch")
def videowatch():
    # 로컬 동영상 경로 설정
    video_path = "streamingvideo.mp4"
    # iFrame으로 동영상 재생
    return render_template("iframe.html", video_path=video_path)


@api.route("/sensor/insert", methods=["POST"])
class sensorinsert(Resource):
    def post(self):
        try:
            result = DBset.sensor_insert(request.get_json())
            return result
        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to insert record into MySQL table: {error}")
            return f"Failed to insert record into MySQL table: {error}"


@api.route("/sensor/select")
class sensorselect(Resource):
    def get(self):
        try:
            data = DBset.sensor_select()

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to select database of MySQL table: {error}")
            return f"Failed to select database of MySQL table: {error}"


@api.route("/normalvideo/select")
class normalselect(Resource):
    def get(self):
        try:
            data = DBset.normal_select()

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to select database of MySQL table: {error}")
            return f"Failed to select database of MySQL table: {error}"


@api.route("/crashvideo/select")
class crashselect(Resource):
    def get(self):
        try:
            data = DBset.crash_select()

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to select database of MySQL table: {error}")
            return f"Failed to select database of MySQL table: {error}"


@api.route("/normalvideo/watch/<strvideodate>")
class watchnormal(Resource):
    def get(self, strvideodate):
        try:
            print(strvideodate)
            DBset.normal_watch(strvideodate)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video at MySQL table: {error}")
            return f"Failed to find video at MySQL table: {error}"

        Videoset.folder_make("down", "", None)

        Videoset.normal_download(strvideodate)

        Videoset.incord()

        return redirect(url_for("videowatch"))
        # return "Please wait incording for 25 seconds"


@api.route("/crashvideo/watch/<strvideodate>")
class watchcrash(Resource):
    def get(self, strvideodate):
        try:
            print(strvideodate)
            DBset.crash_watch(strvideodate)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video at MySQL table: {error}")
            return f"Failed to find video at MySQL table: {error}"

        Videoset.folder_make("down", "", None)

        Videoset.crash_download(strvideodate)

        Videoset.incord()

        return redirect(url_for("videowatch"))
        # return "Please wait incording for 25 seconds"


@api.route("/normalvideo/upload")
class normalvideo(Resource):
    def post(self):
        try:
            file = request.files["normalvideo"]  # 'file'은 업로드된 파일의 key 값입니다.

            Videoset.folder_make("up", "normal", file)

            DBset.normal_upload_insert(file)

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

            Videoset.folder_make("up", "crash", file)

            DBset.crash_upload_insert(file)

            # # 파일 업로드 성공시 메시지 반환
            return jsonify({"message": "File upload success"})

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to video upload: {error}")
            return f"Failed to video upload: {error}"


@api.route("/normalvideo/download/<strvideodate>")
class videodown(Resource):
    def get(self, strvideodate):
        url = Videoset.generate_presigned_url(
            "normal", "normalvideo/" + strvideodate, strvideodate
        )
        file_name = strvideodate
        # send_file 함수로 파일 다운로드를 위한 Response 객체 생성
        response = send_file(urllib.request.urlopen(url), mimetype="video/mp4")
        # 파일 다운로드를 위한 헤더 설정
        response.headers["Content-Disposition"] = f"attachment; filename={file_name}"

        return response


@api.route("/crashvideo/download/<strvideodate>")
class videodown(Resource):
    def get(self, strvideodate):
        url = Videoset.generate_presigned_url(
            "crash", "crashvideo/" + strvideodate, strvideodate
        )
        file_name = strvideodate
        # send_file 함수로 파일 다운로드를 위한 Response 객체 생성
        response = send_file(urllib.request.urlopen(url), mimetype="video/mp4")
        # 파일 다운로드를 위한 헤더 설정
        response.headers["Content-Disposition"] = f"attachment; filename={file_name}"

        return response


@api.route("/normalvideo/find", methods=["POST"])  # 검색기능 만들기만해둠
class selectnormal(Resource):
    def post(self):
        try:
            data = DBset.normal_find(request.get_json())

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video of MySQL table: {error}")
            return f"Failed to find video of MySQL table: {error}"


@api.route("/crashvideo/find", methods=["POST"])
class selectnormal(Resource):
    def post(self):
        try:
            data = DBset.crash_find(request.get_json())

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to find video of MySQL table: {error}")
            return f"Failed to find video of MySQL table: {error}"


# @api.route("/normalvideo/delete/<strvideodate>")  # 영상제거 s3권한이슈로 보류
# class videodel(Resource):
#     def get(self, strvideodate):
#         object = s3r.Object(bucket_name, "normalvideo/" + strvideodate)
#         object.delete()
#         # s3c.delete_object(Bucket=bucket_name, Key="normalvideo/test.mp4")

#         return "video " + strvideodate + " has deleted"


@api.route("/eyes/insert", methods=["POST"])
class eyesinsert(Resource):
    def post(self):
        try:
            strdate, streyesnow = DBset.eyes_insert(request.get_json())
            return {"inserted successfully!": "%s, %s" % (strdate, streyesnow)}
        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to insert record into MySQL table: {error}")
            return f"Failed to insert record into MySQL table: {error}"


@api.route("/eyes/select")
class eyesselect(Resource):
    def get(self):
        try:
            data = DBset.eyes_select()

            return jsonify(data)

        except mysql.connector.Error as error:  # 원인찾기용도
            print(f"Failed to select database of MySQL table: {error}")
            return f"Failed to select database of MySQL table: {error}"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
