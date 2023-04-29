import tflite_runtime.interpreter as tflite
import tflite_runtime as tfl
import cv2
import numpy as np
import time

model = "/home/BlackBoxProject/JunHatest/model.tflite"
interpreter = tflite.Interpreter(model_path=model)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

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

cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    # # 캠이 정상적으로 열렸는지 확인합니다.
    # if not cap.isOpened():
    #     ret, frame = cap.read()
    #     print("카메라를 열 수 없습니다.")
    #     exit()
    # Preprocess the image for input to the tflite model
    resized = cv2.resize(
        frame, (input_details[0]["shape"][2], input_details[0]["shape"][1])
    )
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    img = np.expand_dims(gray, axis=2)
    img = np.expand_dims(img, axis=0)
    img = img.astype("float32") / 255.0

    # Run inference on the preprocessed image
    interpreter.set_tensor(input_details[0]["index"], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]["index"])
    prediction = output[0][0]

    # Display the frame and prediction
    # cv2.imshow("frame", frame)
    time.sleep(0.5)
    print("Prediction:", prediction)

    # Press 'q' to exit the program
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
