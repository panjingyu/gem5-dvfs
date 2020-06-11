#!/usr/bin/env python3

import re
import matplotlib.pyplot as plt

power_file_name = 'power-334-1269.txt'
with open('log/'+power_file_name, 'r') as power_file:
    power = [float(p) for p in power_file.readlines()]

int_pattern = re.compile(r'\d+')
int_match = int_pattern.findall(power_file_name)
assert int_match

power_start = int(int_match[0])
power_end   = int(int_match[1])

smooth_power = []
for i in range(power_start, power_end):
    smooth_power.append((power[i-1]+power[i])/2)

plt.plot(smooth_power)
plt.savefig('power.png')

with open('log/'+'power-332-356.txt', 'r') as power_file_2:
    power2 = [float(p) for p in power_file_2.readlines()]
import numpy as np
print('var:{}'.format(np.var(power2[332:356])))
