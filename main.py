import numpy as np
import time
import signal
import socket
import sys

from Algorithm import DDPG_Algorithm
from Environment import Arm_Env
from Manual import Manual_Control

rl_brain = True    # 是否使用强化学习
test = False        # 是否为测试模式（否则会进行训练）

if rl_brain:
    control = DDPG_Algorithm()
else:
    control = Manual_Control()

def do_exit(sig, stack):
    print("Try to shutdown socket connection")
    control.env.t_server.conn.shutdown(socket.SHUT_RDWR)
    control.env.t_server.conn.close()
    control.env.p_server.conn.shutdown(socket.SHUT_RDWR)
    control.env.p_server.conn.close()
    sys.exit(0)
 
signal.signal(signal.SIGINT, do_exit)
signal.signal(signal.SIGUSR1, do_exit)

for i in range(1000000):
    if test:
        control.test()
    else:
        control.execute()
        # if i % 3 == 1:
        control.train()
    