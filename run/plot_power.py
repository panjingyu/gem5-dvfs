#!/usr/bin/env python3
#coding=utf-8

import re
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
config = {
    "font.sans-serif":'FangSong',
    # "font.size": 14,
    "mathtext.fontset":'stix',
    "font.serif": ['FangSong'],
}
plt.rcParams.update(config)

parseinst_log_name = 'log/parseinst.log'
start_num = exit_num = 0
with open(parseinst_log_name, 'r') as parse_file:
    parse_out_lines = parse_file.readlines()
    for l in parse_out_lines:
        if 'start from' in l:
            start_num = int(re.search('\d+', l).group())
        elif 'exit at' in l:
            exit_num = int(re.search('\d+', l).group())
assert start_num != 0 and exit_num != 0 and start_num != exit_num

power_file_name = 'm5out/powerlist.txt'
with open(power_file_name, 'r') as power_file:
    power = [float(p) for p in power_file.readlines()]

cycle_file_name = 'm5out/cyclelist.txt'
with open(cycle_file_name, 'r') as cycle_file:
    cycle = [int(c) for c in cycle_file.readlines()]

noise_file_name = 'm5out/noiselist.txt'
with open(noise_file_name, 'r') as noise_file:
    noise = [float(n) for n in noise_file.readlines()]
noise_file_name = 'm5out/numsnlist.txt'
with open(noise_file_name, 'r') as numsn_file:
    numsn = [int(n) for n in numsn_file.readlines()]

smooth_power = []
smooth_power_duration = []
frequency = 1000 # MHz
for i in range(start_num, exit_num):
    smooth_power.append((power[i-1]+power[i])/2)
    if i == start_num:
        smooth_power_duration.append(cycle[i]/frequency)
    else:
        smooth_power_duration.append(smooth_power_duration[i-start_num-1] + cycle[i]/frequency)

noise_start = sum(numsn[:start_num])
noise_exit  = sum(numsn[start_num:exit_num]) + noise_start
# noise_time = 0.01 # us
noise_time = smooth_power_duration[-1] / (noise_exit - noise_start)
noise_duration = [noise_time * i for i in range(noise_exit - noise_start)]

figure_save_dir = '/home/pan/Working/'
fig, axs = plt.subplots(2)

axs[0].plot(smooth_power_duration, power[start_num:exit_num])
axs[0].set_title('')
# axs[0].title('电源谐振病毒的功耗曲线时域图')
# axs[0].savefig(figure_save_dir + 'power-PDRV.png')

axs[1].plot(noise_duration, noise[noise_start:noise_exit])
# axs[1].xlabel('时间')
# axs[1].savefig(figure_save_dir + 'noise-PDRV.png')
# axs.clf()

for ax in axs.flat:
    ax.set(xlabel='时间/$\mu s$')
    ax.label_outer()
axs.flat[0].set(ylabel='功率/$W$')
axs.flat[1].set(ylabel='噪声电压/$V$')

fig.savefig(figure_save_dir + 'power-noise-random.png')

# 计算sth版输出的方差
# with open('log/power.txt', 'r') as power_file_2:
#     power2 = [float(p) for p in power_file_2.readlines()]
# import numpy as np
# print('var:{}'.format(np.var(power2[332:356])))
