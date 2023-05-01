import os
import requests


def past_video_list(video_dir):
    prev_video_files = [
        os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".mp4")
    ]

    return prev_video_files


def new_video_list(video_dir, PrevVideoFales):
    new_video_files = [
        os.path.join(video_dir, f)
        for f in os.listdir(video_dir)
        if f.endswith(".mp4") and f not in PrevVideoFales
    ]

    return new_video_files


def different_video_list(NewVideoFiles, PrevVideoFales, url):
    for video_file in NewVideoFiles:
        file_name = os.path.basename(video_file)
        video = {"normalvideo": open(video_file, "rb")}
        response = requests.post(url, files=video)
        print(f"{file_name} uploaded. Server response: {response.text}")

        # 업로드한 비디오 파일을 이전에 업로드한 비디오 파일 목록에 추가
        PrevVideoFales.append(file_name)
