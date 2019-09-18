#!/bin/bash

rm m5out/*
cd run
# g++ -O2 instgen.cc -o instgen.out && ./instgen.out
# arm-linux-gcc -static testout.s -o testout.out
# arm-linux-gcc -static example.s -o example.out

./codegen.py && ./assemblygen.py
arm-linux-gcc -static newgen.s -o newgen.out
cd ..

# CMD=run/testout.out
# CMD=run/example.out
# CMD=tests/test-progs/hello/bin/arm/linux/hello
CMD=run/newgen.out


# use default peripheral parameters
./build/ARM/gem5.opt configs/example/se.py -c $CMD --cpu-type=DerivO3CPU --caches # --l1d_size=32Kb --l1i_size=32Kb --l2cache --l2_size=1024Kb

cd run
./getmaxpower.py
cd ..
