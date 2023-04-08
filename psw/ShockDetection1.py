import subprocess
import os
import datetime

dir_path = "/home/pi/2team/videos/"
cut_path = "/home/pi/2team/videos/ShockVideos//"

now = datetime.datetime.now()
output_filename = now.strftime("%Y%m%d_%H%M%S") + ".mp4"

# 디렉토리 내 모든 파일과 디렉토리의 이름을 얻습니다.
file_list = os.listdir(dir_path)

# 가장 최근에 수정된 파일의 이름과 수정 시간을 저장할 변수를 초기화합니다.
recent_file_name = None
recent_mod_time = 0

# 파일 목록을 반복하면서 수정 시간이 가장 최근인 파일을 찾습니다.
for file_name in file_list:
    file_path = os.path.join(dir_path, file_name)
    mod_time = os.path.getmtime(file_path)
    if mod_time > recent_mod_time:
        recent_file_name = file_name
        recent_mod_time = mod_time

input_file = os.path.join(dir_path, recent_file_name)
output_file = os.path.join(cut_path, output_filename)
start_time = "00:00:05"
end_time = "00:00:10"

cmd = [
    "ffmpeg",
    "-i",
    input_file,
    "-ss",
    start_time,
    "-to",
    end_time,
    "-c",
    "copy",
    output_file,
]

subprocess.run(cmd)
