import cv2
import os
import time
import datetime
import subprocess

os.chdir("psw")

while 1:
    # 캠을 켭니다.
    cap = cv2.VideoCapture(0)

    # 캠이 정상적으로 열렸는지 확인합니다.
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        exit()

    # 저장할 경로와 파일 이름을 지정합니다.
    now = datetime.datetime.now()
    save_path = "videos"
    filename = now.strftime("%Y%m%d_%H%M%S") + ".mp4"

    # 경로가 존재하지 않으면 생성합니다.
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 저장할 경로와 파일 이름을 합칩니다.
    save_file = os.path.join(save_path, filename)

    # FFmpeg을 이용해 저장할 때 사용할 명령어를 지정합니다.
    command = [
        "ffmpeg",
        "-y",  # 덮어쓰기
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "bgr24",
        "-s",
        "640x480",
        "-i",
        "-",
        "-c:v",
        "mpeg4",  # mpeg-4 코덱
        "-preset",
        "fast",
        "-crf",
        "22",
        "-c:v",
        "libx264",  # AVC 비디오 스트림
        "-pix_fmt",
        "yuv420p",
        save_file,
    ]
    # Popen을 이용해 FFmpeg 명령어를 실행할 프로세스를 생성합니다.
    p = subprocess.Popen(command, stdin=subprocess.PIPE)

    # 지정한 시간(초) 동안 비디오를 캡처하고 저장합니다.
    start_time = time.time()
    while (time.time() - start_time) < 200:  # 5분 동안 캡처합니다.
        ret, frame = cap.read()  # 영상을 캡처합니다.

        # 캡처된 영상을 저장합니다.
        if ret == True:
            # FFmpeg 프로세스에 캡처된 프레임을 전달합니다.
            p.stdin.write(frame.tobytes())

            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break

    # 캠과 FFmpeg 프로세스를 종료합니다.
    cap.release()
    p.stdin.close()
    p.wait()


# 창을 닫습니다.
cv2.destroyAllWindows()
