import numpy as np
import time
from Algorithm import DDPG_Algorithm
from Environment import Arm_Env
from Manual import Manual_Control

control = Manual_Control()

for _  in range(1000):
    control.execute()   # step 中有 0.5 秒延迟
    control.train()
