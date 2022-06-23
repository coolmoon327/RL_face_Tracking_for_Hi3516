import numpy as np
from Environment import Arm_Env
import time

class Manual_Control:
    def __init__(self) -> None:
        self.env = Arm_Env()
    
    def execute(self):
        s = self.env.get_state()
        if s is None:
            time.sleep(0.5)
            return
        
        print("state: ",s)

        x1, y1, x2, y2 = s
        x_center = (x1+x2)/2
        y_center = (y1+y2)/2
        w = np.abs(x2 - x1)
        h = np.abs(y2 - y1)

        # 根据 x 调整左右
        act2 = int((1 - x_center) * self.env.action_space[1].n)  # 假设 act2 0-9 是机械臂从最左到最右的位置 (人面对看), 人脸在照片的左边, 说明机械臂应该移动到右边

        # TODO 根据 y_center 与 w*h 调整上下、前后
        pass
        act1 = 9

        action = np.array([act1, act2])
        self.env.step(action=action)
    
    def train(self):
        pass

