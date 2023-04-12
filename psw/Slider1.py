import spidev
import time
import RPi.GPIO as IO

# SPI 인스턴스 spi생성
spi = spidev.SpiDev()
# 라즈베리와 SPI통신 시작
spi.open(0, 0)  # open(bus, device)
# SPI 통신 속도 설정
spi.max_speed_hz = 100000

# MCP3008 채널 중 슬라이드에 연결한 채널 설정
axel_channel = 0
break_channel = 1

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


#
# 회전속도 변화 0~100 사이의 값
def set_motor_speed(speed):
    # 음수가 들어오는 것을 방지하기 위해 abs()함수 사용
    pwm_A.ChangeDutyCycle(abs(speed))


# MCP3008을 통해 전송된 아날로그 데이터를 읽어드림
def readadc(adcnum):  # adcnum: 읽어들일 채널
    # spi.xfer2()함수를 통해 MCP3008에게 3개의 바이트 데이터(start bit, channel select, don't care bit)를
    # 전송하고, MCP3008으로부터 2바이트의 데이터를 수신
    # 이것을 이용하여 10비트 아날로그 값을 계산하여 반환
    # 반환값: 0 ~ 1023
    r = spi.xfer2([1, (8 + adcnum) << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data


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

try:
    while True:
        # readadc 함수로 슬라이드의 SPI데이터를 읽어옴
        axel_value = readadc(axel_channel)
        break_value = readadc(break_channel)
        print("------------------------")
        print(f"axel_Value: {axel_value}    break_Value: {break_value}")

        # 모터 최대속도의 50%로 회전
        set_motor_speed(50)

        currTime = time.time()
        elapsedTime = currTime - prevTime  # 이전 측정 시간으로부터 현재까지의 경과시간
        deltaEncoder = encoderPos - prevEncoderPos  # 변화한 회전수

        # elapsedTime에 360.0을 곱해주어 초를 분으로 변환
        rpm = deltaEncoder / (elapsedTime * 360.0) * 60
        print(f"RPM: {rpm}")

        # 이전 측정 시간과 이전 엔코더 위치를 저장해 둠으로써
        # 다음 측정 시간에서 현재 측정된 시간과 엔코더 위치의 차이를
        # 계산하여 회전 속도를 측정
        # 이전 값과 현재 값을 비교하면서 변화를 측정하는 것을 센서값의 미분이라고 함
        prevTime = currTime
        prevEncoderPos = encoderPos

        time.sleep(0.1)

except KeyboardInterrupt:
    IO.cleanup()
