#!/bin/bash

# execute in gem5 root

timestamp=$(date +%F-%R)

for i in {0..0}
do

    rm m5out/*
    cd run
        ./assemblygen.py --dir codegen --seed $i --inst add
        arm-linux-gcc -static codegen/assembly/${i}.s -o newgen.out
    cd ..

    # select program to execute

    # CMD=tests/test-progs/hello/bin/arm/linux/hello
    CMD=run/newgen.out


    # use default peripheral parameters
    # add debug flag Exec to see exact instuction in execution

    ./build/ARM/gem5.opt 1> log/runse-${i}.log 2>&1 \
        --debug-flags=Exec \
        configs/example/se.py \
        -c $CMD \
        --cpu-type=DerivO3CPU \
        --caches \
        # --l1d_size=32Kb --l1i_size=32Kb --l2cache --l2_size=1024Kb

    paplay /usr/share/sounds/ubuntu/stereo/system-ready.ogg # notification ring of job done
    cd run
        cp ../m5out/powerlist.txt codegen/powerlist/${i}.txt
        chmod a-x codegen/powerlist/${i}.txt # powerlist bug (why is it executable??)
        ./parseinst.py ../log/runse-${i}.log
    cd ..

done