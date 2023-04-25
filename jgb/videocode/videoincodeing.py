import subprocess
import os

local = os.path.dirname(__file__)
dir = os.path.dirname(local)
print(dir)
# 입력 파일 경로
input_file = dir + "/testing.mp4"

# 출력 파일 경로
output_file = dir + "/streamingvideo.mp4"

# ffmpeg 명령어
command = f"ffmpeg -i {input_file} -c:v libx264 -preset veryfast -crf 22 -c:a copy {output_file}"

# ffmpeg 실행
subprocess.call(command, shell=True)
