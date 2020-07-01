#!/bin/bash

# execute in gem5 root

timestamp=$(date +%F-%R)

for i in {0..0}
do

    rm m5out/*
    cd run
        # ./assemblygen.py --dir codegen --seed $i
        # arm-linux-gnueabi-gcc -static  -marm -march=armv7-a -masm-syntax-unified -mfloat-abi=softfp codegen/assembly/${i}.s -o newgen.out
    cd ..

    # select program to execute

    # CMD=tests/test-progs/hello/bin/arm/linux/hello
    CMD=../automotive/basicmath/basicmath_small
    # CMD=../automotive/bitcount/bitcnts
    # CMD=(../automotive/qsort/qsort_small ../automotive/qsort/input_small.dat)
    # CMD=(../automotive/susan/susan ../automotive/susan/input_small.pgm ../automotive/susan/output_small.smoothing.pgm -s)
    # CMD=run/testout.out
    # CMD=run/newgen.out


    # use default peripheral parameters
    # add debug flag Exec to see exact instuction in execution

    time timeout --signal=SIGINT 200 ./build/ARM/gem5.opt 1> log/runse-${i}.log 2>&1 \
        --debug-flags=Exec,ExecUser,ExecMacro \
        configs/example/se.py \
        -c $CMD \
        --cpu-type=DerivO3CPU \
        --caches \
        # --l1d_size=32Kb --l1i_size=32Kb --l2cache --l2_size=1024Kb

    paplay /usr/share/sounds/ubuntu/stereo/system-ready.ogg # notification ring of job done
    ./run/parseinst.py ./log/runse-${i}.log ./m5out/ #--max-power-only

done