#!/usr/bin/python3

import sys

with open('../m5out/powerlist.txt', 'r') as powerlist:
    plist = powerlist.readlines()
    if len(plist) <= 334:
         sys.stderr.write('powerlist seems too small!\n')
         exit(1)
    else:
        print(max([float(p) for p in plist[334:]]))
