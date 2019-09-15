#!/usr/bin/python3

import re

power = []

# with open('../m5out/power.txt') as powerout:
#     for line in powerout:
#         power_m = re.search('(?<=power = )(\d+(\.\d+))', line)
#         if power_m is not None:
#             power.append(float(power_m.group()))

with open('../m5out/powerlist.txt') as powerlist:
    for p in powerlist:
        power.append(float(p))

print(max(power))
