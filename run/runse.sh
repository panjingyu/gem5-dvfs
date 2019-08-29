#!/bin/bash

# ./instgen
arm-linux-gcc -static testout.s -o testout.out
./build/ARM/gem5.opt configs/example/se.py -c testout.out