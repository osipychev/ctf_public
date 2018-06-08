

# TeamConst
""" Defining the constants for agents and teams """
RED = 10
BLUE = 50
GRAY = 90
NUM_BLUE = 4
NUM_RED = 4
NUM_UAV = 0
NUM_GRAY = 10
UAV_STEP = 3
UGV_STEP = 1
UAV_RANGE = 4
UGV_RANGE = 2
UAV_A_RANGE = 0
UGV_A_RANGE = 2

# Model
RL_SUGGESTIONS = False


# MapConst
""" Defining the constants for map and environment """
WORLD_H = 100
WORLD_W = 100
RED_ZONE = 15
RED_AGENT = 20
RED_FLAG = 10
BLUE_ZONE = 55
BLUE_AGENT = 60
BLUE_FLAG = 50
GRAY_AGENT = 95
#OBSTACLE = 100
AERIAL_DENIAL = 90

SUGGESTION = -5
BLACK = -2
UNKNOWN = -1
TEAM1_BACKGROUND = 0
TEAM2_BACKGROUND = 1
TEAM1_UGV = 2
TEAM1_UAV = 3
TEAM2_UGV = 4
TEAM2_UAV = 5
TEAM1_FLAG = 6
TEAM2_FLAG = 7
OBSTACLE = 8
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
              DEAD : (0, 0, 0),
              SELECTED : (122, 77, 25),
              BLACK : (0, 0, 0),
              SUGGESTION : (50, 50, 50),
              COMPLETED : (100, 0, 0)}
