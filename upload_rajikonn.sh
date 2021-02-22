#!/usr/bin/env sh
cd `dirname $0`

ampy -p "/dev/ttyUSB0" put "./rajikonn/main.py"
ampy -p "/dev/ttyUSB0" put "./rajikonn/ble_advertising.py"
ampy -p "/dev/ttyUSB0" put "./rajikonn/ble_simple_peripheral.py"
