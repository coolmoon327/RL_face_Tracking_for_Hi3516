import numpy as np
from Environment import Arm_Env
import time

class Manual_Control:
    def __init__(self) -> None:
        self.env = Arm_Env()
        self.rst_timeout = 0
    
    def execute(self):
        s = self.env.get_state()
        if s is None:
            self.rst_timeout += 1
            if self.rst_timeout == 5:
                print("No human face detected. Now reseting the robot arm.")
                self.env.reset()
                self.rst_timeout = 0
            return
        
        self.rst_timeout = 0
        right, left, bottom, top, vs, hs = s

        if bottom > 1080 or top > 1080:
            print("Error! Y is more than 1080!")
        if right > 1920 or left > 1920:
            print("Error! X is more than 1920!")

        x_center = (left + right)/2
        y_center = (top + bottom)/2
        w = np.abs(right - left)
        h = np.abs(bottom - top)

        print("state: ", s, ", xc:", x_center, ", yc:", y_center, ", w:", w, ", h: ", h)

        # 根据 x 调整左右
        # act2 = int(x_center/self.env.screen_width * self.env.action_space[1].n)
        # act2 = np.clip(int((x_center/self.env.screen_width-0.5)*5 + hs), 0, 9)
        offset_x = x_center/self.env.screen_width-0.5
        if offset_x > 0.1:
            act2 = hs + 1 + offset_x * 5
        elif offset_x < -0.1:
            act2 = hs - 1 + offset_x * 5
        else:
            act2 = hs
        act2 = np.clip(int(act2), 0, 10)

        # 根据 y 调整上下
        # act1 = int(y_center/self.env.screen_height * self.env.action_space[0].n)
        # act1 = np.clip(int(-(y_center/self.env.screen_height-0.5)*10 + vs), 0, 19)
        offset_y = y_center/self.env.screen_height-0.5
        if offset_y > 0.1:
            act1 = vs - 1 - offset_y * 5
        elif offset_x < -0.1:
            act1 = vs + 1 - offset_y * 5
        else:
            act1 = vs
        act1 = np.clip(int(act1), 0, 10)

        action = np.array([act1, act2])

        print("Action: ", action)

        self.env.step(action=action)
    
    def train(self):
        pass

