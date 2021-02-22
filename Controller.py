# -*- coding: utf-8 -*-
import pygame
import bleak
import asyncio
import queue
import threading
import pygame.locals as pl
import struct
import sys

# ble_simple_peripheral.pyにあるものと一致するようにする
UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

# スレッド間で共有するためのグローバル変数
power = queue.Queue()


# 通信のための関数
async def central(loop):
    try:
        while True:
            # デバイスのスキャンと選択をする
            while True:
                print("Scanning...")
                devices = await bleak.discover()

                for i, v in enumerate(devices):
                    print(f"{i}: {v}")

                inp = input("Select a device to connect : ")

                # 何も入力されなかったらもう一回スキャンする
                if inp == "":
                    continue
                # 何かが入力されたなら
                else:
                    # デバイスのリストからデバイスを取得する
                    try:
                        device = devices[int(inp)]
                    # リストの大きさを超えた数字が入力されたか、int型に変換できない文字列を入力されたらエラーを表示する
                    except (IndexError, ValueError):
                        print("Input a valid number.")
                    # デバイスの取得が成功したらループから脱出する
                    else:
                        break

            print(f"Selected : {device}")

            try:
                # デバイスに接続する
                async with bleak.BleakClient(device, loop=loop) as client:
                    # 接続が終わるまで待つ
                    await client.is_connected()
                    print("Connected")

                    while True:
                        # LeftPower, RightPower をBytes型に変換する
                        d = power.get()
                        data = struct.pack("hh", d[0], d[1])
                        # データを送信する
                        await client.write_gatt_char(UUID, data)
                        # 送信したデータを表示する
                        print(f"Write: {data}")
            # エラーが起きたら
            except (AttributeError, bleak.BleakError):
                # エラーメッセージを表示する
                print("Error disconnected.")
    # Ctrl + C で終了する
    except KeyboardInterrupt:
        pass


# コントローラー
class Controller:
    def __init__(self):
        # pygameを初期化する
        pygame.init()
        # ジョイスティックを格納するための変数
        self.joystick = None
        # ウインドウの初期化
        self.screen = pygame.display.set_mode((500, 500))
        # FPSを一定に保つための時計
        self.clock = pygame.time.Clock()
        # 入力のバッファ
        self.input = [0.0, 0.0]
        # FPS(フレーム毎秒)
        self.FPS = 30
        
        self.pre_power = (-10.0, -10.0)

        # 背景色
        self.BGColor = (200, 200, 200)
        # 入力に使うキー
        self.UPKEYS = [pl.K_w, pl.K_UP]
        self.DOWNKEYS = [pl.K_s, pl.K_DOWN]
        self.LEFTKEYS = [pl.K_a, pl.K_LEFT]
        self.RIGHTKEYS = [pl.K_d, pl.K_RIGHT]
        # 接続されているジョイスティックを取得する
        self.init_joystick()

    def init_joystick(self):
        # 接続されているジョイスティックが0以上なら0番目のジョイスティックを設定する
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    # キー入力とジョイスティックの入力を受け取る
    def input_handler(self):
        # 押されているキーを取得
        pressed_keys = pygame.key.get_pressed()

        self.input = [0.0, 0.0]

        for upkey in self.UPKEYS:
            if pressed_keys[upkey]:
                self.input[1] = 1.0
                break
        for downkey in self.DOWNKEYS:
            if pressed_keys[downkey]:
                self.input[1] = -1.0
                break
        for leftkey in self.LEFTKEYS:
            if pressed_keys[leftkey]:
                self.input[0] = -1.0
                break
        for rightkey in self.RIGHTKEYS:
            if pressed_keys[rightkey]:
                self.input[0] = 1.0
                break

        # ジョイスティックがあれば
        if self.joystick:
            self.input[0] += self.joystick.get_axis(0)
            self.input[1] -= self.joystick.get_axis(1)
            self.input[0] = max(-1.0, min(1.0, self.input[0]))
            self.input[1] = max(-1.0, min(1.0, self.input[1]))

    def apply_powers(self):
        lp = max(-1023, min(1023, int(self.input[1] * 1023 + self.input[0] * 512)))
        rp = max(-1023, min(1023, int(self.input[1] * 1023 + self.input[0] * -512)))
        if (lp, rp) != self.pre_power:
            power.put((lp, rp))
            self.pre_power = (lp, rp)

    def draw(self):
        scr_size = self.screen.get_size()
        sf = pygame.Surface(size=scr_size)
        sf.fill(self.BGColor)
        pygame.draw.circle(sf, (255, 0, 0), (int(scr_size[0] / 2 + self.input[0] * 200),
                                             int(scr_size[1] / 2 + self.input[1] * -200)), 10)
        self.screen.blit(sf, self.screen.get_rect())
        pygame.display.update()

    def run(self):
        while True:
            self.clock.tick(self.FPS)
            self.input_handler()
            self.apply_powers()
            self.draw()
            for event in pygame.event.get():
                if event.type == pl.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pl.KEYDOWN:
                    if event.key == pl.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                        

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    cent = threading.Thread(target=loop.run_until_complete, args=(central(loop),))
    cent.setDaemon(True)
    cent.start()
    con = Controller()
    con.run()
