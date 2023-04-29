import spidev
import time
import RPi.GPIO as IO
import requests
import json
import datetime
import pymysql

# SPI 인스턴스 spi생성
spi = spidev.SpiDev()
# 라즈베리와 SPI통신 시작
spi.open(0, 0)  # open(bus, device)
# SPI 통신 속도 설정
spi.max_speed_hz = 100000

# MCP3008 채널 중 슬라이드에 연결한 채널 설정
axel_channel = 0
break_channel = 1


# MCP3008을 통해 전송된 아날로그 데이터를 읽어드림
def readadc(adcnum):  # adcnum: 읽어들일 채널
    # spi.xfer2()함수를 통해 MCP3008에게 3개의 바이트 데이터(start bit, channel select, don't care bit)를
    # 전송하고, MCP3008으로부터 2바이트의 데이터를 수신
    # 이것을 이용하여 10비트 아날로그 값을 계산하여 반환
    # 반환값: 0 ~ 1023
    r = spi.xfer2([1, (8 + adcnum) << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data


# 모터구동을 위한 PWM핀 설정
# 엔코더값을 받아올 핀 설정
PWM_A = 18
encPinA = 23
encPinB = 24
IO.setmode(IO.BCM)
IO.setwarnings(False)
IO.setup(encPinA, IO.IN, pull_up_down=IO.PUD_UP)
IO.setup(encPinB, IO.IN, pull_up_down=IO.PUD_UP)
IO.setup(PWM_A, IO.OUT)

# PWM 제어 설정
# PWM(모터의 핀, 주파수)
pwm_A = IO.PWM(PWM_A, 1000)
pwm_A.start(0)

encoderPos = 0  # 엔코더의 현재 회전수
prevEncoderPos = 0  # 이전에 측정된 회전수
prevTime = time.time()  # 이전에 측정된 시간


# 회전속도 변화 0~100 사이의 값
def set_motor_speed(speed):
    # 음수가 들어오는 것을 방지하기 위해 abs()함수 사용
    pwm_A.ChangeDutyCycle(abs(speed))


# A채널의 신호를 비교하여 encoderPos값을 증가 또는 감소
def encoderA(channel):
    # encoderPos를 다른 함수에서도 사용하기 위해 전역 변수로 선언
    global encoderPos

    if IO.input(encPinA) == IO.input(encPinB):
        encoderPos += 1
    else:
        encoderPos -= 1


# B채널의 신호를 비교하여 encoderPos값을 중가 또는 감소
def encoderB(channel):
    global encoderPos

    if IO.input(encPinA) == IO.input(encPinB):
        encoderPos -= 1
    else:
        encoderPos += 1


IO.add_event_detect(encPinA, IO.BOTH, callback=encoderA)
IO.add_event_detect(encPinB, IO.BOTH, callback=encoderB)


def change_motor_speed(axel_value, break_value):
    # axel_value와 break_value의 평균 값을 구하고 1023으로 나누어 비율 값으로 변환
    ratio = (axel_value - break_value) / (2 * 1023)
    # 모터의 최대 속도는 100으로 가정
    if ratio < 0:
        speed = 0
    else:
        speed = ratio * 100
    # 모터의 속도 변경
    set_motor_speed(speed)


def send_log(speed, axel_value, break_value):
    now = datetime.datetime.now()
    strnow = now.strftime("%Y%m%d_%H%M%S")
    url = "http://43.201.154.195:5000/sensor/insert"
    data = {
        "strdate": strnow,
        "straccel": str(axel_value),
        "strbreak": str(break_value),
        "intspeed": speed,
    }

    headers = {"Content-type": "application/json"}
    data_json = json.dumps(data)

    requests.post(url, data=data_json, headers=headers)


# 데이터베이스 연결 초기 설정
mydb = pymysql.connect(
    host="localhost", user="root", password="0000", charset="utf8", database="Sensor"
)
mycursor = mydb.cursor()


def insert_db(date, hourv, exel_percent, break_percent):
    exel_percent = str(exel_percent) + "%"
    break_percent = str(break_percent) + "%"
    sql = "INSERT INTO sensordata ( DATE, SPEED, EXEL_VALUE, BREAK_VALUE) VALUES (%s, %s,%s, %s);"
    # val = (date, hour, exel_percent, break_percent)
    mycursor.execute(sql, [date, hourv, exel_percent, break_percent])

    mydb.commit()


try:
    while True:
        # readadc 함수로 슬라이드의 SPI데이터를 읽어옴
        axel_value = readadc(axel_channel)
        break_value = readadc(break_channel)
        axel_v = (axel_value / 1023) * 100
        break_v = (break_value / 1023) * 100
        print("------------------------")
        print(f"axel_Value: {axel_v}%    break_Value: {break_v}%")

        change_motor_speed(axel_value, break_value)

        currTime = time.time()
        elapsedTime = currTime - prevTime  # 이전 측정 시간으로부터 현재까지의 경과시간
        deltaEncoder = encoderPos - prevEncoderPos  # 변화한 회전수

        # elapsedTime에 360.0을 곱해주어 초를 분으로 변환
        rpm = deltaEncoder / (elapsedTime * 360.0) * 60
        hour = rpm / 2
        print(f"RPM: {abs(rpm)}  시속:{abs(hour)}")

        # 이전 측정 시간과 이전 엔코더 위치를 저장해 둠으로써
        # 다음 측정 시간에서 현재 측정된 시간과 엔코더 위치의 차이를
        # 계산하여 회전 속도를 측정
        # 이전 값과 현재 값을 비교하면서 변화를 측정하는 것을 센서값의 미분이라고 함
        prevTime = currTime
        prevEncoderPos = encoderPos

        # send_log(speed,axel_v,break_v)

        now = datetime.datetime.now()
        strnow = now.strftime("%Y%m%d_%H%M%S")
        insert_db(strnow, hour, round(axel_v, 2), round(break_v, 2))

        time.sleep(0.1)

except KeyboardInterrupt:
    pwm_A.stop()
    IO.cleanup()
    spi.close()
