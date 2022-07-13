import numpy as np

class Servo:
    def __init__(self):
        pass
    
    @classmethod
    def get_operation(self, vert_op, hori_op) -> str:
        """
            vert_op: 0~9 竖直位置, 从下到上
            hori_op: 0~9 水平位置, 从左往右
            return: 舵机操作指令
        """
        time = "T0250!"

        pwm_h = str(int(-hori_op * 600/10 + 1800))
        while len(pwm_h) < 4: pwm_h = "0" + pwm_h
        oph = "#000P" + pwm_h + time
        
        pwm_v1 = str(int(vert_op * 600/10 + 900))
        pwm_v2 = str(int(vert_op * 1100/10 + 500))
        pwm_v3 = str(int(-vert_op * 500/10 + 1400))
        while len(pwm_v1) < 4: pwm_v1 = "0" + pwm_v1
        while len(pwm_v2) < 4: pwm_v2 = "0" + pwm_v2
        while len(pwm_v3) < 4: pwm_v3 = "0" + pwm_v3
        opv = "#001P" + pwm_v1 + time + "#002P" + pwm_v2 + time + "#005P" + pwm_v3 + time

        # pwm_v1 = str(int(vert_op * 600/10 + 900))
        # pwm_v3 = str(int(-vert_op * 600/10 + 1500))
        # while len(pwm_v1) < 4: pwm_v1 = "0" + pwm_v1
        # while len(pwm_v3) < 4: pwm_v3 = "0" + pwm_v3
        # opv = "#001P" + pwm_v1 + time + "#002P1600" + time + "#005P" + pwm_v3 + time

        op = "{" + oph + opv + "}"
        return op
    
    @classmethod
    def reset_operation(self) -> str:
        """
            return: reset 位置对应的舵机操作指令
        """
        # op = "{#000P1500T1000!#001P1200T1000!#002P1050T1000!#005P1150T1000!}"
        op = Servo.get_operation(5, 5)

        # left: {#000P1800T1000!#001P1200T1000!#002P1050T1000!#005P1150T1000!} 
        # right: {#000P1200T1000!#001P1200T1000!#002P1050T1000!#005P1150T1000!} 
        # bottom: {#000P1500T1000!#001P0900T1000!#002P0500T1000!#005P1400T1000!} 
        # top: {#000P1500T1000!#001P1500T1000!#002P1600T1000!#005P0900T1000!}

        # 0 左右 越大越向左 (机械臂的左)
        # 1 最下 越大越向下
        # 2 中间 越大越往后
        # 5 最上 越大越向上

        return op
    