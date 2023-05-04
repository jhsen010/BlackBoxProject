import os
from videocode import video_func

local = os.path.dirname(__file__)
dir = os.path.dirname(local)


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
