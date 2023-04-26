import os
import boto3
import subprocess

local = os.path.dirname(__file__)
dir = os.path.dirname(local)

strlocal = dir + "/videostreaming/downloadedvideo.mp4"


def video_init():
    s3c = boto3.client("s3")  # 비디오 다운용

    s3r = boto3.resource("s3")  # 비디오 업용
    bucket_name = "mobles3"
    bucket = s3r.Bucket(bucket_name)

    return s3c, s3r, strlocal, bucket, bucket_name


def gen(strlocal):
    with open(strlocal, "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            yield data


def incord():
    # 입력 파일 경로
    input_file = dir + "/videostreaming/downloadedvideo.mp4"

    # 출력 파일 경로
    output_file = dir + "/videostreaming/streamingvideo.mp4"

    # ffmpeg 명령어
    command = f"ffmpeg -i {input_file} -c:v libx264 -preset veryfast -crf 22 -c:a copy {output_file}"

    # ffmpeg 실행
    subprocess.call(command, shell=True)
