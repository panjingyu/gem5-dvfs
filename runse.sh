#!/bin/bash

# execute in gem5 root: ./runse.sh 1> runse-$(date +%F-%R).log 2>&1 &

timestamp=$(date +%F-%R)

for i in {1..10}
do

    rm m5out/*
    cd run
        # g++ -O2 instgen.cc -o instgen.out && ./instgen.out
        # arm-linux-gcc -static testout.s -o testout.out
        # arm-linux-gcc -static example.s -o example.out

        ./assemblygen.py --dir codegen --seed $i
        arm-linux-gcc -static codegen/${i}.s -o newgen.out
    cd ..

    # CMD=run/testout.out
    # CMD=run/example.out
    # CMD=tests/test-progs/hello/bin/arm/linux/hello
    CMD=run/newgen.out


    # use default peripheral parameters
    ./build/ARM/gem5.opt configs/example/se.py -c $CMD --cpu-type=DerivO3CPU --caches 1> /dev/null \
    # --l1d_size=32Kb --l1i_size=32Kb --l2cache --l2_size=1024Kb

    cd run
        cp ../m5out/powerlist.txt codegen/powerlist/${i}.txt
        echo ${i}:$(./getmaxpower.py) >> maxpower-${timestamp}.log
    cd ..

done