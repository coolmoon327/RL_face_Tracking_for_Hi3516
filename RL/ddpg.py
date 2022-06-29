import os
import sys

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.autograd import Variable
import torch.nn.functional as F

def soft_update(target, source, tau):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(target_param.data * (1.0 - tau) + param.data * tau)

def hard_update(target, source):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(param.data)

GPU_AVAILABLE = torch.cuda.is_available()

def push_to_gpu(input):
    try:
        output = input.cuda()
    except RuntimeError as exception:
        if "out of memory" in str(exception):
            print("GPU 显存不足，执行显存清理后重新将对象推入 gpu。")
            torch.cuda.empty_cache()
            output = push_to_gpu(input)
        else:
            raise exception
    return output


"""
From: https://github.com/pytorch/pytorch/issues/1959
There's an official LayerNorm implementation in pytorch now, but it hasn't been included in 
pip version yet. This is a temporary version
This slows down training by a bit
"""
class LayerNorm(nn.Module):
    def __init__(self, num_features, eps=1e-5, affine=True):
        super(LayerNorm, self).__init__()
        self.num_features = num_features
        self.affine = affine
        self.eps = eps

        if self.affine:
            self.gamma = nn.Parameter(torch.Tensor(num_features).uniform_())
            self.beta = nn.Parameter(torch.zeros(num_features))

    def forward(self, x):
        shape = [-1] + [1] * (x.dim() - 1)
        mean = x.view(x.size(0), -1).mean(1).view(*shape)
        std = x.view(x.size(0), -1).std(1).view(*shape)

        y = (x - mean) / (std + self.eps)
        if self.affine:
            shape = [1, -1] + [1] * (x.dim() - 2)
            y = self.gamma.view(*shape) * y + self.beta.view(*shape)
        return y

nn.LayerNorm = LayerNorm


class Actor(nn.Module):
    def __init__(self, hidden_size, num_inputs, action_space):
        super(Actor, self).__init__()
        self.action_space = action_space
        num_outputs = action_space.shape[0]

        self.linear1 = nn.Linear(num_inputs, hidden_size)
        self.ln1 = nn.LayerNorm(hidden_size)

        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.ln2 = nn.LayerNorm(hidden_size)
        
        self.mu = nn.Linear(hidden_size, num_outputs)
        # self.mu.weight.data.mul_(.1)
        # self.mu.bias.data.mul_(.1)

    def forward(self, inputs):
        x = inputs
        x = self.linear1(x)
        x = self.ln1(x)
        x = F.relu(x)
        x = self.linear2(x)
        x = self.ln2(x)
        x = F.relu(x)
        mu = torch.tanh(self.mu(x))
        return mu

class Critic(nn.Module):
    def __init__(self, hidden_size, num_inputs, action_space):
        super(Critic, self).__init__()
        self.action_space = action_space
        num_outputs = action_space.shape[0]

        self.linear1 = nn.Linear(num_inputs, hidden_size)
        self.ln1 = nn.LayerNorm(hidden_size)

        self.linear2 = nn.Linear(hidden_size+num_outputs, hidden_size)
        self.ln2 = nn.LayerNorm(hidden_size)

        self.V = nn.Linear(hidden_size, 1)
        self.V.weight.data.mul_(0.1)
        self.V.bias.data.mul_(0.1)

    def forward(self, inputs, actions):
        x = inputs
        x = self.linear1(x)
        x = self.ln1(x)
        x = F.relu(x)

        x = torch.cat((x, actions), 1)
        
        x = self.linear2(x)
        x = self.ln2(x)
        x = F.relu(x)
        
        V = self.V(x)
        return V

class DDPG(object):
    def __init__(self, gamma, tau, hidden_size, num_inputs, action_space, lr_actor=1e-4, lr_critic=1e-3):

        self.num_inputs = num_inputs
        self.action_space = action_space

        self.actor = Actor(hidden_size, self.num_inputs, self.action_space)
        self.actor_target = Actor(hidden_size, self.num_inputs, self.action_space)
        self.actor_perturbed = Actor(hidden_size, self.num_inputs, self.action_space)
        self.actor_optim = Adam(self.actor.parameters(), lr=lr_actor)

        self.critic = Critic(hidden_size, self.num_inputs, self.action_space)
        self.critic_target = Critic(hidden_size, self.num_inputs, self.action_space)
        self.critic_optim = Adam(self.critic.parameters(), lr=lr_critic)

        if GPU_AVAILABLE:
            self.actor = push_to_gpu(self.actor)
            self.actor_target = push_to_gpu(self.actor_target)
            self.actor_perturbed = push_to_gpu(self.actor_perturbed)
            self.critic = push_to_gpu(self.critic)
            self.critic_target = push_to_gpu(self.critic_target)

        self.gamma = gamma
        self.tau = tau

        hard_update(self.actor_target, self.actor)  # Make sure target is with the same weight
        hard_update(self.critic_target, self.critic)


    def select_action(self, state, action_noise=None, param_noise=None):
        """
        返回的是 [-pi/2, pi/2] 之间的数，需要在外部进行采样
        :param state:
        :param action_noise:
        :param param_noise:
        :return:
        """
        state = Variable(state)
        if GPU_AVAILABLE:
            state = push_to_gpu(state)

        self.actor.eval()
        if param_noise is not None: 
            mu = self.actor_perturbed(state)
        else:
            mu = self.actor(state)

        self.actor.train()
        mu = mu.data

        if GPU_AVAILABLE:
            mu = mu.cpu()

        if action_noise is not None:
            mu += torch.Tensor(action_noise.noise())

        return mu


    def update_parameters(self, batch):
        state_batch = Variable(torch.cat(batch.state))
        action_batch = Variable(torch.cat(batch.action))
        reward_batch = Variable(torch.cat(batch.reward))
        mask_batch = Variable(torch.cat(batch.mask))
        next_state_batch = Variable(torch.cat(batch.next_state))
        
        if GPU_AVAILABLE:
            state_batch = push_to_gpu(state_batch)
            action_batch = push_to_gpu(action_batch)
            reward_batch = push_to_gpu(reward_batch)
            mask_batch = push_to_gpu(mask_batch)
            next_state_batch = push_to_gpu(next_state_batch)

        try:
            next_action_batch = self.actor_target(next_state_batch)
            next_state_action_values = self.critic_target(next_state_batch, next_action_batch).detach()

            reward_batch = reward_batch.unsqueeze(1)
            mask_batch = mask_batch.unsqueeze(1)
            expected_state_action_batch = reward_batch + (self.gamma * mask_batch * next_state_action_values)

            self.critic_optim.zero_grad()

            state_action_batch = self.critic((state_batch), (action_batch))

            value_loss = F.mse_loss(state_action_batch, expected_state_action_batch)
            value_loss.backward()
            self.critic_optim.step()

            self.actor_optim.zero_grad()

            policy_loss = -self.critic((state_batch),self.actor((state_batch)))
            
            policy_loss = policy_loss.mean()
            policy_loss.backward()
            self.actor_optim.step()

            soft_update(self.actor_target, self.actor, self.tau)
            soft_update(self.critic_target, self.critic, self.tau)

            return value_loss.item(), policy_loss.item()
        
        except RuntimeError as exception:
            if "out of memory" in str(exception):
                print("GPU 显存不足，跳过本次训练。")
                if hasattr(torch.cuda,"empty_cache"):
                    torch.cuda.empty_cache()
            else:
                raise exception

    def perturb_actor_parameters(self, param_noise):
        """Apply parameter noise to actor model, for exploration"""
        hard_update(self.actor_perturbed, self.actor)
        params = self.actor_perturbed.state_dict()
        for name in params:
            if 'ln' in name: 
                pass 
            param = params[name]
            param += torch.randn(param.shape) * param_noise.current_stddev

    def save_model(self, env_name, suffix="", actor_path=None, critic_path=None):
        if not os.path.exists('RL/models/'):
            os.makedirs('RL/models/')

        if actor_path is None:
            actor_path = "RL/models/ddpg_actor_{}_{}.pkl".format(env_name, suffix)
        if critic_path is None:
            critic_path = "RL/models/ddpg_critic_{}_{}.pkl".format(env_name, suffix)
        print('Saving models to {} and {}'.format(actor_path, critic_path))
        torch.save(self.actor.state_dict(), actor_path)
        torch.save(self.critic.state_dict(), critic_path)

    def load_model(self, actor_path, critic_path):
        print('Loading models from {} and {}'.format(actor_path, critic_path))
        if actor_path is not None:
            if GPU_AVAILABLE:
                self.actor.load_state_dict(torch.load(actor_path))
            else:
                self.actor.load_state_dict(torch.load(actor_path, map_location='cpu'))
            hard_update(self.actor_target, self.actor)
            for parameters in self.actor.parameters():
                print(parameters)
        if critic_path is not None: 
            if GPU_AVAILABLE:
                self.critic.load_state_dict(torch.load(critic_path))
            else:
                self.critic.load_state_dict(torch.load(critic_path, map_location='cpu'))
            hard_update(self.critic_target, self.critic)
            for parameters in self.critic.parameters():
                print(parameters)