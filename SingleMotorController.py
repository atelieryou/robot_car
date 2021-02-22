# -*- coding: utf-8 -*-
import bleak
import asyncio
import queue
import threading
import pygame
import pygame.locals as pl
import struct
import sys
import time

# ble_simple_peripheral.pyにあるものと一致するようにする
UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

# スレッド間で共有するためのグローバル変数
power = queue.Queue()


async def select_device():
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
            
        return device

    print(f"Selected : {device}")


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
                        data = struct.pack("hh", d, 0)
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


def controller():
    pygame.init()
    screen = pygame.display.set_mode((100, 50))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 50)
    
    pre_velocity = -1
    
    while True:
        clock.tick(30)
        
        sf = pygame.Surface(size=screen.get_size())
        sf.fill((255, 255, 255))
        screen.blit(sf, screen.get_rect())
        
        pressed_keys = pygame.key.get_pressed()
        
        velocity = 0
        
        if pressed_keys[pl.K_UP]:
            velocity += 1023
            screen.blit(font.render("↑", True, (0, 0, 0)), (0, 0))
        
        if pressed_keys[pl.K_DOWN]:
            velocity -= 1023
            screen.blit(font.render("↓", True, (0, 0, 0)), (50, 0))
            
        pygame.display.update()
        
        if pre_velocity != velocity:
            pre_velocity = velocity
            power.put(velocity)
        
        for event in pygame.event.get():
            if event.type == pl.QUIT:
                pygame.quit()
                sys.exit()
    

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    cent = threading.Thread(target=loop.run_until_complete, args=(central(loop),))
    cent.setDaemon(True)
    cent.start()
    controller()

