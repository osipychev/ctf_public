import unittest
import gym
import gym_cap

import numpy as np
import random

ENV_NAME = 'cap-v0'

def repeat(times):
    " Wrapper for multiple test"
    def repeatwrapper(f):
        def callwrapper(*args):
            for i in range(times):
                f(*args)
        return callwrapper
    return repeatwrapper

class TestBuild(unittest.TestCase):

    def testBuild(self):
        " Test if environment build for any random seeds"
        test_epoch = 50 
        for epoch in range(test_epoch):
            env = gym.make(ENV_NAME)

    def testMapSize(self):
        " Test if the environment can handle map size. (10~20)"
        test_epoch = 32 
        test_maxstep = 100
        for size in range(10, 20):
            for epoch in range(test_epoch):
                env = gym.make(ENV_NAME, map_size=size)

class TestAgentTeamMemory(unittest.TestCase):
    pass

class TestAgentIndivMemory(unittest.TestCase):
    pass

class TestAgentGetObs(unittest.TestCase):

    @repeat(10)
    def testFrequency(self):
        " Communication frequency test"
        env = gym.make(ENV_NAME)
        env.COM_FREQUENCY = random.random()# Try random frequency
        env.reset()
        for entity in env.team_blue+env.team_red:
            entity.get_obs(env)
                
    @repeat(10)
    def testComAir(self):
        " Communication between ground and air test"
        env = gym.make(ENV_NAME)
        env.NUM_UAV = 2
        env.COM_AIR = True
        env.reset()
        for entity in env.team_blue+env.team_red:
            entity.get_obs(env)

    @repeat(10)
    def testComGround(self):
        " Communication between ground and air test"
        env = gym.make(ENV_NAME)
        env.NUM_UAV = 2
        env.COM_GROUND = True
        env.reset()
        for entity in env.team_blue+env.team_red:
            entity.get_obs(env)

if __name__ == '__main__':
    unittest.main()
