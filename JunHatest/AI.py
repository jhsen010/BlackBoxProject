import tflite_runtime.interpreter as tflite
import tflite_runtime as tfl
import cv2
import numpy as np
import requests
import json
import datetime


now = datetime.datetime.now()
timestamp_str = now.strftime("%Y%m%d_%H%M%S")  # DB이름
url = "http://43.201.154.195:5000/eyes/insert"  # api서버 url

# lite 모델 가져오기
model = "/home/BlackBoxProject/JunHatest/final.tflite"
interpreter = tflite.Interpreter(model_path=model)  # TFlite model을 memory에 올림
interpreter.allocate_tensors()  # tensor initailization = 텐서 초기화

input_details = (
    interpreter.get_input_details()
)  # input에 대한 다양한 정보 호출(index, input.shape ,data type)
output_details = interpreter.get_output_details()


cap = cv2.VideoCapture(2)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("카메라카 켜지지않음")
        break

    # frame 을 모델 input 형태로 변환
    resized = cv2.resize(
        frame, (input_details[0]["shape"][2], input_details[0]["shape"][1])
    )
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    img = np.expand_dims(gray, axis=2)  # (x,y,1)
    img = np.expand_dims(img, axis=0)  # (1,x,y,1)
    img = img.astype("float32") / 255.0

    interpreter.set_tensor(
        input_details[0]["index"], img
    )  # TFlite model이 예측 가능하도록 image를 input layer의 위치(index)에 넣어주어 처리
    interpreter.invoke()  # TFLite 모델에서 추론 프로세스를 실행하여 출력 텐서를 생성.
    output = interpreter.get_tensor(output_details[0]["index"])  # 출력 텐서

    prediction = output[0][0]
    result = 0
    if prediction >= 0.5:
        result = 1
    else:
        result = 0

    # cv2.imshow("frame", frame)
    print("Prediction:", result)
    data = {
        "strdate": timestamp_str,
        "streyesnow": str(result),
    }
    headers = {"Content-type": "application/json"}
    data_json = json.dumps(data)
    response = requests.post(
        url, data=data_json, headers=headers
    )  # 원격 서버에 예측과 함께 요청을 보냄

    if cv2.waitKey(1) & 0xFF == ord("q"):
        cap.release()
        cv2.destroyAllWindows()
        break


# cap = cv2.VideoCapture(0)


# while cap.isOpened():
#     # 프레임 읽기
#     ret, frame = cap.read()
#     if not cap.isOpened():
#         print("카메라를 열 수 없습니다.")
#     else:
#         print("카메라가 정상적으로 열렸습니다.")
#     # 이미지 크기 조정 및 전처리
#     resized = cv2.resize(frame, (26, 34), interpolation=cv2.INTER_AREA)
#     x = np.expand_dims(resized, axis=0)
#     x = x / 255.0  # 이미지 픽셀 값을 0~1로 정규화합니다.
#     # frame = cv2.resize(frame, (224, 224))
#     # # 예측
#     # frame = np.expand_dims(frame, axis=0)  # add batch size dimension
#     pred = model.predict(x)[0]
#     result = np.argmax(pred)  # 가장 높은 확률의 클래스를 선택합니다.

#     # 예측 결과를 화면에 출력
#     if result == 0:
#         cv2.putText(
#             frame, "awake", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
#         )
#     else:
#         cv2.putText(
#             frame, "drowsy", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
#         )

#     # 화면에 출력
#     cv2.imshow("frame", frame)
#     if cv2.waitKey(1) == ord("q"):  # q를 입력하면 종료합니다.
#         break

# cap.release()
# cv2.destroyAllWindows()
