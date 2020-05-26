# gem5-dvfs notes

## Envrionment

- `gcc` and `g++` version: `5.5.0`
- `arm-linux-gcc` version: `4.5.1`
- other requrements of gem5 are up-to-date

## Ideas

gem5给出的power stats并不是clock-cycle-wise的，因此反复执行同一指令（操作数不同）
每个指令的能耗 = power / (IPC * frequency) = power * CPI / frequency

## 代码解释

- `gem5-stable-629fe6e6c781.tar.bz2`：gem5源码
- `/gem5`：我们对gem5的修改，注意修改路径，用绝对路径
- `/gem5/parameter`:该文件夹内是各种参数，需要修改的是parameter.config
- `/gem5/parameter/parameter.config`:该文件内是修改的参数，powerin表示功耗输入文件，powerout表示功耗输出文件，powerfreq表示多少个cycle求一次功耗，powervol是电压。其他的是求noise的，不用管
- `/gem5/configs/common/Simulation.py`: 该文件对gem5仿真流程的控制，让其powerfreq个cycle输出一段stats，来计算功耗。
- `/gem5/src/base/stats/text.cc`: 该文件是修改gem5的stats，计算功耗的模型。
- `/gem5/instgen.cc`:该文件的功能是指令空间生成代码，输入13个维度，输出ARM的代码

## Other notes

gem5似乎在编译时会往build/target文件夹中的Address.hh写入依赖于编译时的路径的环境变量等。
`m5out/powerlist.txt`中前334行记录的应该是loader的功率，应当剔除
### parameter notes
- `counter_input_o3.txt`: counter names, used in `CounterIn()`
- `bayes_o3.txt`: pre-trained parameters, used in `ParamIn()`; final line is for constant term (1)
- `label_o3.txt`: used in `FormulaIn()`