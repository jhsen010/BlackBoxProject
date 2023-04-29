from dotenv import load_dotenv
import os
import mysql.connector
from videocode import video_func

local = os.path.dirname(__file__)
dir = os.path.dirname(local)


def rds_connect():
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
        return conn
    except Exception as e:
        print("Unable to connect to RDS.")
        print(e)


def folder_make(mode, NorC, file, bucket):
    if mode == "down":
        if not os.path.exists(dir + "/videostreaming"):  # 없으면 만들어
            os.makedirs(dir + "/videostreaming")
        for file_name in os.listdir(dir + "/videostreaming"):
            file_path = os.path.join(dir + "/videostreaming", file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)  # 파일 삭제

    elif mode == "up":
        if not os.path.exists(dir + "/videoupload"):  # 없으면 만들어
            os.makedirs(dir + "/videoupload")
        file.save(dir + "/videoupload/" + file.filename)

        if NorC == "normal":
            video_func.normal_upload(file, bucket)
        elif NorC == "crash":
            video_func.crash_upload(file, bucket)

        file_path = dir + "/videoupload/" + file.filename
        os.remove(file_path)
