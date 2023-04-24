import RPi.GPIO as GPIO
import time

# 핀 번호 설정
LEFT_ENCODER_PIN = 18  # 왼쪽 엔코더 신호선 (BCM 기준 2번 핀)
MOTOR_PIN1 = 23  # 모터 제어핀1 (BCM 기준 3번 핀)
MOTOR_PIN2 = 24  # 모터 제어핀2 (BCM 기준 4번 핀)

# 모터 제어 주기 및 주파수 설정
PWM_FREQ = 50  # PWM 주파수
PWM_CYCLE = 100  # PWM 주기 (0~100)

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_ENCODER_PIN, GPIO.IN)
GPIO.setup(MOTOR_PIN1, GPIO.OUT)
GPIO.setup(MOTOR_PIN2, GPIO.OUT)

# PWM 객체 생성
motor_pwm1 = GPIO.PWM(MOTOR_PIN1, PWM_FREQ)
motor_pwm2 = GPIO.PWM(MOTOR_PIN2, PWM_FREQ)


# 모터 회전 함수 (CW: 시계방향, CCW: 반시계방향)
def motor_rotate(CW=True, speed=PWM_CYCLE):
    if CW:
        motor_pwm1.start(0)
        motor_pwm2.start(speed)
    else:
        motor_pwm1.start(speed)
        motor_pwm2.start(0)


# RPM 측정 함수
def get_rpm(pin, duration=1):
    pulse_count = 0  # 펄스 개수
    pulse_duration = 0  # 펄스 폭

    # 펄스 개수 측정
    def count_pulse(channel):
        nonlocal pulse_count
        pulse_count += 1

    GPIO.add_event_detect(pin, GPIO.RISING, callback=count_pulse)

    # 주어진 시간 동안 펄스 폭 측정
    start_time = time.time()
    while time.time() - start_time < duration:
        pulse_duration += GPIO.input(pin)
    end_time = time.time()

    # 펄스 개수, 펄스 폭으로 RPM 계산
    rpm = pulse_count / ((end_time - start_time) * 60)
    return rpm


try:
    while True:
        motor_rotate(CW=True, speed=50)  # 모터 회전 (속도 50)
        rpm = get_rpm(LEFT_ENCODER_PIN)  # 왼쪽 엔코더 RPM 측정
        print(f"RPM: {rpm}")
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
