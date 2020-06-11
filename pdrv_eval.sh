#!/bin/bash

rm m5out/*

PV_EXE=run/testout.out

# PV_EXE=run/pdrv.out
# ./run/pdrv_gen.py --pv-only \
# && arm-linux-gcc -static run/pdrv.s -o $PV_EXE

time (./build/ARM/gem5.opt 1> log/runse-pv.log 2>&1 \
    --debug-flags=Exec \
    configs/example/se.py \
    -c $PV_EXE \
    --cpu-type=DerivO3CPU \
    --caches \
    # --l1d_size=32Kb --l1i_size=32Kb --l2cache --l2_size=1024Kb
)
./run/parseinst.py ./log/runse-pv.log ./m5out/ --max-power-only
