import numpy as np
import time
from gym import spaces
import socket
import threading

from Servo import Servo

GAMMA = .9
MAX_OUNOISE_SIGMA = .8
custom_ounoise_sigma = 0.3   # 如果是 -1，则从 MAX_OUNOISE_SIGMA 开始逐渐减小探索度，否则按照指定的值来设置探索度
param_noise_scale = 0.5

state_dim = 4        # 四个状态 (right, left, bottom, top)
action_dim = 2       # 两组预设 (竖直方向的预设 + 水平方向的预设)

screen_width = 1920
screen_height = 1080

### socket
self_ip = "0.0.0.0"
t_port = 3516
p_port = 3861
BUFFER_SIZE = 20

recv_buffer = []

threadLock = threading.Lock()

class TCP_Server(threading.Thread):
    def __init__(self, IP, Port):
        threading.Thread.__init__(self)
        self.IP = IP
        self.Port = Port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((IP, Port))

    def run(self):
        self.sock.listen(10)
        self.conn, self.peer_addr = self.sock.accept()
        print(f'Port: {self.Port} Connection address: ', self.peer_addr)

        if self.Port == t_port:
            while 1:
                try:
                    recv = self.conn.recv(BUFFER_SIZE).decode()
                except:
                    print("Connection broke out! Waiting for another connection...")
                    self.conn, self.peer_addr = self.sock.accept()
                    print(f'Port: {self.Port} Connection address: ', self.peer_addr)
                # print(f'Time: {time.time()} | Port: {self.Port} | Receive data: ', recv)
                threadLock.acquire()
                recv_buffer.append(recv)
                threadLock.release()
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()

        elif self.Port == p_port:
            pass

    def send(self, msg: str):
        try:
            self.conn.send(msg.encode('utf-8'))
            # print("Sent ", msg)
            return True
        except:
            print(f"Cannot send message: {msg}")
            return False


class Arm_Env(object):
    def __init__(self):
        self.action_space = spaces.Tuple(
            [spaces.Discrete(11), spaces.Discrete(11)]
        )
        self.n_actions = self.action_space.__len__()
        self.n_observations = state_dim + 2     # 还有现在的 vertical 和 horizon 位置

        self.vs = 5
        self.hs = 5

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.t_server = TCP_Server(self_ip, t_port)
        self.p_server = TCP_Server(self_ip, p_port)

        self.t_server.start()
        self.p_server.start()

    def get_state(self):
        # 通过 socket 获取初始状态 s
        threadLock.acquire()

        try:
            recv = recv_buffer[-1]  # 只取最新的状态
            recv_buffer.clear()     # 清空 buffer
            s = recv.split(",")     # str -> str list
            s = list(map(int, s)) # str list -> float list
            s.append(self.vs)
            s.append(self.hs)
            s = np.array(s)
        except:
            s = None

        threadLock.release()
        return s

    def get_reward(self, s):
        right, left, bottom, top, vs, hs = s

        #计算矩阵中心距离屏幕中心的距离
        sxc = self.screen_width/2
        syc = self.screen_height/2
        x_center = (left + right)/2
        y_center = (top + bottom)/2
        dis = np.sqrt((x_center - sxc)**2 + (y_center - syc)**2)

        #计算 w h 的大小, 以及它们距离标准大小的差别
        w_std = 0.3 * self.screen_width
        h_std = 0.35 * self.screen_height
        w = np.abs(right - left)
        h = np.abs(bottom - top)
        dif = np.sqrt((h - h_std)**2 + (w - w_std)**2)

        return 100 - (dis + dif)

    def execute(self, action):
        # 将 action 翻译成 p 板能识别的格式
        act_msg = Servo.get_operation(action[0], action[1])
        
        # 执行 action
        if self.p_server.send(act_msg):
            self.vs = action[0]
            self.hs = action[1]

    def seed(self, seed):
        np.random.seed(seed)
    
    def close(self):
        self.reset()

    def reset(self):
        #  通过 socket 复位机械臂
        self.vs = 10
        self.hs = 5
        act_msg = Servo.reset_operation()
        self.p_server.send(act_msg)
        return self.get_state()
    
    def step(self, action):
        # 1. 执行 action
        self.execute(action)
    
        # 2. 获取状态转移
        time.sleep(0.5) # TODO 调整等待的时间
        s_ = self.get_state()

        # 3. 根据 s_ 计算 reward
        if s_ is not None:
            reward = self.get_reward(s_)
        else:
            reward = -100.

        # 4. 补充完整标准 step 函数的返回值 (虽然没有使用)
        done = False
        info = {}

        return s_, reward, done, info
