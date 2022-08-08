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
            if self.rst_timeout == 4:
                print("No human face detected. Now reseting the robot arm.")
                self.env.reset()
                self.rst_timeout = 0
            time.sleep(0.5)
            return
        self.rst_timeout = 0
        
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
        offset_x = x_center/self.env.screen_width-0.5
        offset_y = y_center/self.env.screen_height-0.5

        print("state: ", s, ", xc:", x_center, ", yc:", y_center, ", w:", w, ", h: ", h)

        # # 根据 x 调整左右
        # # act2 = int(x_center/self.env.screen_width * self.env.action_space[1].n)
        # # act2 = np.clip(int((x_center/self.env.screen_width-0.5)*5 + hs), 0, 9)
        # offset_x = x_center/self.env.screen_width-0.5
        # if offset_x > 0.07:
        #     act2 = hs + 1 + np.abs(offset_x) * 4
        # elif offset_x < -0.07:
        #     act2 = hs - 1 - np.abs(offset_x) * 4
        # else:
        #     act2 = hs
        # act2 = np.clip(int(act2), 0, 10)

        # # 根据 y 调整上下
        # # act1 = int(y_center/self.env.screen_height * self.env.action_space[0].n)
        # # act1 = np.clip(int(-(y_center/self.env.screen_height-0.5)*10 + vs), 0, 19)
        # offset_y = y_center/self.env.screen_height-0.5
        # if offset_y > 0.01:
        #     act1 = vs - 1 #- abs(offset_y) * 7
        # elif offset_x < -0.01:
        #     act1 = vs + 1 #+ abs(offset_y) * 7
        # else:
        #     act1 = vs
        # act1 = np.clip(int(act1), 0, 10)

        # action = np.array([act1, act2])

        action = np.array([0, 0])
        if offset_y > 0.05: dy = -1    # 脸在下面, 参数越小越下
        elif offset_y < -0.05: dy = 1
        else: dy = 0
        if offset_x > 0.05: dx = 1     # 脸在右边, 参数越大越右
        elif offset_x < -0.05: dx = -1
        else: dx = 0
        
        nx = 1
        ny = 1 
        if np.abs(offset_x)>0.3:
            nx = 2
        if np.abs(offset_x)>0.6:
            nx = 3
        if np.abs(offset_x)>0.8:
            nx = 4
        if np.abs(offset_y)>0.3:
            ny = 2
        if np.abs(offset_y)>0.6:
            ny = 3
        if np.abs(offset_y)>0.8:
            ny = 4
        
        action[0] = dy * ny + vs
        action[1] = dx * nx + hs
        action = np.clip(action, 0, 10)
        action = np.round(action)
        
        print("Action: ", action)

        self.env.step(action=action, test=True)
        time.sleep(0.6)
    
    def test(self):
        self.execute()

    def train(self):
        pass

