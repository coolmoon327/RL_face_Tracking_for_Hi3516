import numpy as np

class Servo:
    def __init__(self):
        pass
    
    def get_operation(self, hori_op, vert_op) -> str:
        """
            hori_op: 0~9 水平位置
            vert_op: 0~19 竖直位置
            return: 舵机操作指令
        """    
        pass
        op = "#000P0500T0000"
        return op
    
    def reset_operation(self) -> str:
        """
            return: reset 位置对应的舵机操作指令
        """
        pass
        op = "#000P0500T0000"
        return op
    