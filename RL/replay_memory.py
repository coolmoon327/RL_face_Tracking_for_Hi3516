import os
import pickle
import random
from collections import namedtuple
from turtle import position

# Taken from
# https://github.com/pytorch/tutorials/blob/master/Reinforcement%20(Q-)Learning%20with%20PyTorch.ipynb

Transition = namedtuple('Transition', ('state', 'action', 'mask', 'next_state', 'reward'))


class ReplayMemory(object):

    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        """Saves a transition."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)
    
    def save_memory(self, env_name, suffix="", mem_path=None):
        if not os.path.exists('RL/mem/'):
            os.makedirs('RL/mem/')

        if mem_path is None:
            mem_path = "RL/mem/mem_{}_{}.pkl".format(env_name, suffix)
        print('Saving memory to {}'.format(mem_path))
        with open(mem_path, 'ab') as f:
            f.seek(0)
            f.truncate()
            pickle.dump(self.memory, f)
        conf_path = "RL/mem/conf_{}_{}.pkl".format(env_name, suffix)
        with open(conf_path, 'ab') as f:
            f.seek(0)
            f.truncate()
            pickle.dump([self.capacity, self.position], f)

    def load_memory(self, mem_path):
        print('Loading memory from {}'.format(mem_path))
        with open(mem_path, 'rb') as f:
            self.memory = pickle.load(f)
        last_slash_index = mem_path.rfind('/')
        mem_index = mem_path.rfind('mem_')
        conf_path = "{}/conf_{}".format(mem_path[0:last_slash_index],mem_path[mem_index+4:])
        with open(conf_path, 'rb') as f:
            self.capacity, self.position = pickle.load(f)
