import cv2
import os
import time
import datetime


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
    filename = now.strftime("%Y%m%d_%H%M%S") + ".avi"

    # 경로가 존재하지 않으면 생성합니다.
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 저장할 경로와 파일 이름을 합칩니다.
    save_file = os.path.join(save_path, filename)

    # 비디오 코덱을 설정합니다.
    fourcc = cv2.VideoWriter_fourcc(*"H264")

    # 비디오 파일을 저장할 객체를 생성합니다.
    out = cv2.VideoWriter(save_file, fourcc, 20.0, (640, 480))

    # 지정한 시간(초) 동안 비디오를 캡처하고 저장합니다.
    start_time = time.time()
    while (time.time() - start_time) < 300:  # 30초 동안 캡처합니다.
        ret, frame = cap.read()  # 영상을 캡처합니다.

        # 캡처된 영상을 저장합니다.
        if ret == True:
            out.write(frame)

            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break

    # 캠과 파일 저장 객체를 닫습니다.
    cap.release()
    out.release()

# 창을 닫습니다.
cv2.destroyAllWindows()
