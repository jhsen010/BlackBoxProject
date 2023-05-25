import datetime
import numpy as np
import matplotlib.pyplot as plt
from keras.layers import Input, Activation, Conv2D, Flatten, Dense, MaxPooling2D
from keras.models import Model, load_model
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
import tensorflow as tf
from tensorflow import keras

plt.style.use("dark_background")

# 데이터셋 가져오기
x_train = np.load("/content/drive/MyDrive/datasets/x_train.npy").astype(np.float32)
y_train = np.load("/content/drive/MyDrive/datasets/y_train.npy").astype(np.float32)
x_val = np.load("/content/drive/MyDrive/datasets/x_val.npy").astype(np.float32)
y_val = np.load("/content/drive/MyDrive/datasets/y_val.npy").astype(np.float32)

print(x_train.shape, y_train.shape)
print(x_val.shape, y_val.shape)
"""
(2586, 26, 34, 1) (2586, 1)
(288, 26, 34, 1) (288, 1)
"""
# image generator
# eye dataset이기 때문에 카메라에 찍힐수있는 눈의 모든 변수에 대비
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,  # 0~1로 정규화
    rotation_range=20,  # 회전각도 20도
    width_shift_range=0.2,  # 이미지의 너비에 최대 20%까지 수평이동
    height_shift_range=0.2,  # 수직이동
    shear_range=0.2,  # 전단변환 : 한축을따라 이미지를 기울이고 다른축은 고정
)

val_datagen = ImageDataGenerator(rescale=1.0 / 255)  # 정규화

train_generator = train_datagen.flow(x=x_train, y=y_train, batch_size=32, shuffle=True)

val_generator = val_datagen.flow(x=x_val, y=y_val, batch_size=32, shuffle=False)

inputs = Input(shape=(26, 34, 1))

net = Conv2D(32, kernel_size=3, strides=1, padding="same", activation="relu")(
    inputs
)  # 특징 추출에 유리한 con2D사용
net = tf.keras.layers.BatchNormalization()(net)  # 수렴 속도를 높히기 위해
net = MaxPooling2D(pool_size=2)(net)  # 특징을 가져가되 데이터 축소


net = Conv2D(64, kernel_size=3, strides=1, padding="same", activation="relu")(net)
net = tf.keras.layers.BatchNormalization()(net)
net = MaxPooling2D(pool_size=2)(net)

net = Conv2D(128, kernel_size=3, strides=1, padding="same", activation="relu")(net)
net = tf.keras.layers.BatchNormalization()(net)
net = MaxPooling2D(pool_size=2)(net)

net = Flatten()(net)  # 데이터를 1줄로 나열 ,Dense는 1줄의 데이터만 받음

net = Dense(512)(net)
net = Activation("relu")(net)  # batchnomalization이랑 잘 맞는 비선형함수 relu를 사용
net = Dense(1)(net)
outputs = Activation("sigmoid")(net)  # 눈을 감는다=0,뜬다=1 / 거의 0아니면 1로 수렴하는 sigmoid 사용

model = Model(inputs=inputs, outputs=outputs)

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["acc"])

# model.summary()

start_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

model.fit_generator(
    train_generator,
    epochs=50,
    validation_data=val_generator,
    callbacks=[
        ModelCheckpoint(
            "models/%s.h5" % (start_time),
            monitor="val_acc",
            save_best_only=True,
            mode="max",
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_acc",
            factor=0.2,
            patience=10,
            verbose=1,
            mode="auto",
            min_lr=1e-05,
        ),
    ],
)
# ModelCheckpoint : 학습동안 일정한 간격으로 모델의 가중치를 저장, 최상의 성능을 보인 모델을 선택.
# ReduceLROnPlateau : 학습률을 동적으로 조정하여 학습을 최적화


# ------------------------------------------그래프-------------------------------------------
from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn as sns

model = load_model("models/%s.h5" % (start_time))

y_pred = model.predict(x_val / 255.0)
y_pred_logical = (y_pred > 0.5).astype(np.int)

print("test acc: %s" % accuracy_score(y_val, y_pred_logical))
cm = confusion_matrix(y_val, y_pred_logical)
sns.heatmap(cm, annot=True)


# ------------------------------------------Lite 변환-------------------------------------------
import tensorflow as tf
import random
import tqdm
import cv2
import glob

# 변수로 저장되어 있는 모델을, TFLite 모델로 변환
converter = tf.lite.TFLiteConverter.from_keras_model(model)


def representative_data_gen():
    image = glob.glob(
        "/content/drive/MyDrive/datasets/yang/*.jpg"
    )  # 이 파일에 저장된 모든 jpg파일의 path
    random.shuffle(image)

    for image in tqdm.tqdm(image):
        img = cv2.imread(image)
        img = cv2.resize(img, dsize=(26, 34), interpolation=cv2.INTER_AREA)
        img = cv2.cvtColor(
            img, cv2.COLOR_BGR2GRAY
        )  # 제가 사용한 모델은 흑백 이미지를 사용했기 때문에 GRAY로 변환했습니다.
        img = np.expand_dims(img, -1)  # input과 데이터 형태 동일하게 맞춤
        img = np.expand_dims(img, 0)  # input과 데이터 형태 동일하게 맞춤
        img = img.astype(np.float32) / 255.0
        yield [img]


# INT8 양자화 설정
converter.representative_dataset = representative_data_gen
converter.target_spec.supported_types = [tf.int8]
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# 모델 양자화
tflite_model = converter.convert()

# 변환된 모델을 .tflite 파일에 저장
open("/content/drive/MyDrive/datasets/final.tflite", "wb").write(tflite_model)
