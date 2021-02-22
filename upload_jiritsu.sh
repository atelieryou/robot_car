#!/usr/bin/env sh
cd `dirname $0`

ampy -p "/dev/ttyUSB0" put "./jiritsu/main.py"
