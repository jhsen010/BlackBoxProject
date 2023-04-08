import RPi.GPIO as IO
import time
import datetime
from moviepy.video.io.VideoFileClip import VideoFileClip
import os


def button(channel):
    # 디렉토리 경로
    dir_path = "videos"
    cut_path = "ShockVideos"

    # 디렉토리 내 모든 파일과 디렉토리의 이름을 얻습니다.
    file_list = os.listdir(dir_path)

    # 가장 최근에 수정된 파일의 이름과 수정 시간을 저장할 변수를 초기화합니다.
    recent_file_name = ""
    recent_mod_time = 0.0

    # 파일 목록을 반복하면서 수정 시간이 가장 최근인 파일을 찾습니다.
    for file_name in file_list:
        file_path = os.path.join(dir_path, file_name)
        mod_time = os.path.getmtime(file_path)
        if mod_time > recent_mod_time:
            recent_file_name = file_name
            recent_mod_time = mod_time

    # 비디오 클립 객체 생성
    video = VideoFileClip(os.path.join(dir_path, recent_file_name))

    # 비디오의 총 길이
    total_duration = video.duration

    # 비디오 끝부분 길이
    end_duration = total_duration - video.duration

    # 자를 시작 시간과 끝 시간
    start_time = end_duration - 10  # 초
    end_time = end_duration  # 초

    # 자를 부분 추출
    cut_video = video.subclip(start_time, end_time)

    now = datetime.datetime.now()
    filename = now.strftime("%Y%m%d_%H%M%S") + ".avi"

    # 자른 비디오 파일 저장
    cut_video.write_videofile(os.path.join(cut_path, filename), codec="libx264")


IO.setmode(IO.BCM)
IO.setwarnings(False)
button_pin = 14

IO.setup(button_pin, IO.IN, pull_up_down=IO.PUD_DOWN)

IO.add_event_detect(button_pin, IO.RISING, callback=button, bouncetime=300)

while 1:
    time.sleep(0.1)
