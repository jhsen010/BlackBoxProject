import os
import boto3
import subprocess
import threading
from flask import request


class Videofunc:
    def __init__(self):
        self.local = os.path.dirname(__file__)
        self.dir = os.path.dirname(self.local)
        self.strlocal = self.dir + "/videostreaming/downloadedvideo.mp4"
        self.s3c = boto3.client("s3")  # 비디오 다운용
        self.s3r = boto3.resource("s3")  # 비디오 업용
        self.bucket_name = "mobles3"
        self.bucket = self.s3r.Bucket(self.bucket_name)

    def video_init(self):
        return self.s3c, self.s3r, self.bucket, self.bucket_name

    def folder_make(self, mode, NorC, file):
        if mode == "down":
            if not os.path.exists(self.dir + "/videostreaming"):  # 없으면 만들어
                os.makedirs(self.dir + "/videostreaming")
            for file_name in os.listdir(self.dir + "/videostreaming"):
                file_path = os.path.join(self.dir + "/videostreaming", file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)  # 파일 삭제

        elif mode == "up":
            if not os.path.exists(self.dir + "/videoupload"):  # 없으면 만들어
                os.makedirs(self.dir + "/videoupload")
            file.save(self.dir + "/videoupload/" + file.filename)

            if NorC == "normal":
                self.normal_upload(file)
            elif NorC == "crash":
                self.crash_upload(file)

            file_path = self.dir + "/videoupload/" + file.filename
            os.remove(file_path)

    def incord_thread(self):
        # 입력 파일 경로
        input_file = self.dir + "/videostreaming/downloadedvideo.mp4"

        # 출력 파일 경로
        output_file = self.dir + "/videostreaming/streamingvideo.mp4"

        # ffmpeg 명령어
        command = f"ffmpeg -i {input_file} -c:v libx264 -preset veryfast -crf 22 -c:a copy {output_file}"

        # ffmpeg 실행
        subprocess.call(command, shell=True)

    def incord(self):
        # 쓰레드 생성
        t = threading.Thread(
            target=self.incord_thread
        )  # target=self.incord_thread 여기다 () 달아버리면 쓰레드 정상 작동 안됨
        t.start()

    def normal_download(self, strvideodate):
        self.bucket.download_file(
            "normalvideo/" + strvideodate,
            self.strlocal,
        )

    def crash_download(self, strvideodate):
        self.bucket.download_file(
            "crashvideo/" + strvideodate,
            self.strlocal,
        )

    def normal_upload(self, file):
        # 파일 ec2에서 s3로 업로드하기
        local_file = self.dir + "/videoupload/" + file.filename
        obj_file = "normalvideo/" + file.filename  # S3 에 올라갈 파일명
        self.bucket.upload_file(local_file, obj_file)

    def crash_upload(self, file):
        # 파일 ec2에서 s3로 업로드하기
        local_file = self.dir + "/videoupload/" + file.filename
        obj_file = "crashvideo/" + file.filename  # S3 에 올라갈 파일명
        self.bucket.upload_file(local_file, obj_file)

    def generate_presigned_url(self, mode, object_name, strvideodate, expiration=3600):
        if mode == "normal":
            response = self.s3c.generate_presigned_url(
                "get_object",
                Params={"Bucket": "mobles3", "Key": "normalvideo/" + strvideodate},
                ExpiresIn=expiration,
            )
        elif mode == "crash":
            response = self.s3c.generate_presigned_url(
                "get_object",
                Params={"Bucket": "mobles3", "Key": "crashvideo/" + strvideodate},
                ExpiresIn=expiration,
            )
        return response
