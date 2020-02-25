# gem5-dvfs notes

## Envrionment

- `gcc` and `g++` version: `5.5.0`
- `arm-linux-gcc` version: `4.5.1`
- other requrements of gem5 are up-to-date

## Ideas

1、在Gem5中修改DVFS，即根据功耗动态调节电压和频率，所以需要知道ARM的最大功耗。
所以想使用GAN网络来生成最大功耗的代码。

2、最大功耗的求解和论文"System-level_Max_Power_SYMPO_-_A_Systematic_Approa"类似，设定一个特定的代码空间，
通过遗传算法来搜索代码空间的最佳组合来寻求最值。这个类似的工作我们已经做过了，是使用模拟退火算法进行的。

3、该github代码是使用GAN网络来生成测试浏览器漏洞的代码（可能），我们可以类似的做一个GAN网络
来生成，详见[link](https://github.com/13o-bbr-bbq/machine_learning_security/blob/master/Generator)。

GAN网络的输入是一维的数字，每个数字代表不同的指令。

代码解释：

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
