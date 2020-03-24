#!/usr/bin/env python3

import sys

power = []
with open('../m5out/powerlist.txt', 'r') as powerlist:
    plist = powerlist.readlines()
    if len(plist) <= 334:
         sys.stderr.write('powerlist seems too small!\n')
         exit(1)
    else:
        power = plist[334:]
assert power

log_name = sys.argv[1]

inst_lines = []
with open(log_name, 'r') as log_file:
    log_lines = log_file.readlines()
    main_mark = False
    for l in log_lines:
        if not main_mark and '@main' in l:
            main_mark = True
            inst_lines.append(l)
        elif main_mark and 'system.cpu' in l:
            # after @main
            inst_lines.append(l)

print(len(inst_lines))
print(len(power))