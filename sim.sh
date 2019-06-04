#!/bin/bash

M5_PATH=/home/pan/DVFS/arm-system-2013-07 ./build/ARM/gem5.opt --debug-flags=DVFS,EnergyCtrl \
  --debug-file=dfvs_debug.log configs/example/fs.py --cpu-type=AtomicSimpleCPU \
  -n 2 --machine-type=VExpress_EMM --kernel=/home/pan/DVFS/linux-arm-legacy/vmlinux \
  --dtb-filename=/home/pan/DVFS/linux-arm-legacy/arch/arm/boot/dts/\
vexpress-v2p-ca15-tc1-gem5_dvfs_2cpus.dtb \
  --disk-image=/home/pan/DVFS/arm-system-2013-07/disks/arm-ubuntu-natty-headless.img \
  --cpu-clock=\['1 GHz','750 MHz','500 MHz'\]