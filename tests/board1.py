# -*- coding: utf-8 -*-
"""
Created on Tue May 14 17:25:41 2019

@author: shamith2
"""

import gym 
import policy.roomba
import policy.random
import numpy as np


# Team Constants
""" Defining the constants for agents and teams """

RED = 10
BLUE = 50
GRAY = 90
NUM_BLUE = 4
NUM_RED = 4
NUM_UAV = 0
NUM_GRAY = 0
UAV_STEP = 3
UGV_STEP = 1
UAV_RANGE = 4
UGV_RANGE = 3
UAV_A_RANGE = 0
UGV_A_RANGE = 2

# boolean constants 

blue_win = False
red_win = False
first = True

###############################################################################

# environment constants
""" Defining the constants for agents and environment """

env = gym.make("cap-v0") # initialize the environment
policy_blue = policy.roomba.PolicyGen(env.get_map, env.get_team_blue)
policy_red = policy.random.PolicyGen(env.get_map, env.get_team_red)
mode = "random"

###############################################################################

# Model Constants

RL_SUGGESTIONS = False

STOCH_TRANSITIONS = False
STOCH_ATTACK = False
STOCH_ZONES = False

###############################################################################

# Map Constants
""" Defining the constants for map and environment """

dim = 20
in_seed = 2
rand_zones = STOCH_ZONES
np_random = np.random

TEAM1_BACKGROUND = 0
TEAM2_BACKGROUND = 1
TEAM1_UGV = 2
TEAM1_UAV = 3
TEAM2_UGV = 4
TEAM2_UAV = 5
TEAM3_UGV = 15
TEAM1_FLAG = 6
TEAM2_FLAG = 7
OBSTACLE = 8

###############################################################################

SUGGESTION = -5
BLACK = -2
UNKNOWN = -1
DEAD = 9
SELECTED = 10
COMPLETED = 11

COLOR_DICT = {UNKNOWN : (200, 200, 200),
              TEAM1_BACKGROUND : (0, 0, 120),
              TEAM2_BACKGROUND : (120, 0, 0),
              TEAM1_UGV : (0, 0, 255),
              TEAM1_UAV : (0, 0, 255),
              TEAM2_UGV : (255, 0, 0),
              TEAM2_UAV :  (255, 0, 0),
              TEAM1_FLAG : (0, 255, 255),
              TEAM2_FLAG : (255, 255, 0),
              OBSTACLE : (120, 120, 120),
              TEAM3_UGV : (180, 180, 180),
              DEAD : (0, 0, 0),
              SELECTED : (122, 77, 25),
              BLACK : (0, 0, 0),
              SUGGESTION : (50, 50, 50),
              COMPLETED : (100, 0, 0)}

###############################################################################