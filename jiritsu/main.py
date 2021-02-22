# coding: utf-8
import time
import machine

# ピンの初期化
a1 = machine.Pin(18, machine.Pin.OUT)
a2 = machine.Pin(19, machine.Pin.OUT)

b1 = machine.Pin(16, machine.Pin.OUT)
b2 = machine.Pin(17, machine.Pin.OUT)

pin_pwm_a = machine.Pin(21, machine.Pin.OUT)
pin_pwm_b = machine.Pin(4, machine.Pin.OUT)

# PWMの初期化
pwm_a = machine.PWM(pin_pwm_a)
pwm_b = machine.PWM(pin_pwm_b)


# モーターを動かすための関数
def moter(left, right):
    # 値が -1023 から 1023 に収まるようにする
    left = int(min(max(-1023, int(left)), 1023))
    right = int(min(max(-1023, int(right)), 1023))

    if 0 < right:
        a1.on()
        a2.off()
    else:
        a1.off()
        a2.on()
    if 0 < left:
        b1.on()
        b2.off()
    else:
        b1.off()
        b2.on()

    pwm_a.duty(abs(right))
    pwm_b.duty(abs(left))


def turn(degree):
    # 1秒で何度旋回するか 各自で調節すること
    deg_per_sec = 120

    if 0 < degree:
        moter(1023, -1023)
    if degree < 0:
        moter(-1023, 1023)

    # 時間 = 角度 / 角速度
    # (abs(degree) / deg_per_sec / 1000) ミリ秒待つ
    # ms はミリ秒(1秒の1000分の1)という意味
    time.sleep_ms(int(abs(degree) / deg_per_sec * 1000))
    moter(0, 0)


def forward(cm):
    # 1秒で何センチメートル進むか 各自で調節すること
    cm_per_sec = 10

    moter(1023, 1023)
    # 時間 = 距離 / 速さ
    # ms はミリ秒(1秒の1000分の1)という意味
    time.sleep_ms(int(abs(cm) / cm_per_sec * 1000))
    moter(0, 0)


# 四角形を描くように移動する
for i in range(4):
    forward(60)
    turn(90)
