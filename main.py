import numpy as np
import time
import signal
import socket
import sys

from Algorithm import DDPG_Algorithm
from Environment import Arm_Env
from Manual import Manual_Control

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

for _  in range(1000):
    control.execute()   # step 中有 0.5 秒延迟
    control.train()
    time.sleep(0.5)
