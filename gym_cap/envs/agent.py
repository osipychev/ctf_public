# from gym import error, spaces, utils
# from gym.utils import seeding
# from .cap_view2d import CaptureView2D
from .const import *
import numpy as np
# from .create_map import CreateMap
#from .enemy_ai import EnemyAI


class Agent:
    """This is a parent class for all agents.
    It creates an instance of agent in specific location"""

    def __init__(self, loc, map_only, team_number):
        """
        Constructor

        Parameters
        ----------
        self    : object
            Agent object
        loc     : list
            [X,Y] location of unit
        """
        self.isAlive = True
        self.x, self.y = loc
        self.step = UGV_STEP
        self.range = UGV_RANGE
        self.a_range = UGV_A_RANGE
        self.air = False
        #self.ai = EnemyAI(map_only)
        self.team = team_number
        self.move_selected = False

    def move(self, action, env, team_home):
        """
        Moves each unit individually. Checks if action is valid first.

        Parameters
        ----------
        self        : object
            CapEnv object
        action      : string
            Action the unit is to take
        env         : list
            the environment to move units in
        team_home   : list
            easily place the correct home tiles
        """
        if not self.isAlive:
            return
        
        if action == "X":
            pass
        
        elif action in ["N", "S", "E", "W"]:
            # Air moves
            new_coord = {"N": [self.x, self.y - self.step],
                         "S": [self.x, self.y + self.step],
                         "E": [self.x + self.step, self.y],
                         "W": [self.x - self.step, self.y]}
            new_coord = new_coord[action]

            # Out of bound 
            length, width = env.shape
            if new_coord[0] < 0: new_coord[0] = 0
            if new_coord[1] < 0: new_coord[1] = 0
            if new_coord[0] >= length: new_coord[0] = length-1
            if new_coord[1] >= width: new_coord[1] = width-1

            # Not able to move
            if (self.x, self.y) == new_coord \
                or (self.air and env[new_coord[0]][new_coord[1]] in [TEAM1_UAV, TEAM2_UAV]) \
                or (not self.air and env[new_coord[0]][new_coord[1]] in [OBSTACLE, TEAM1_UGV, TEAM2_UGV]):
                    return

            # Make a movement
            env[self.x][self.y] = team_home[self.x][self.y]
            self.x, self.y = new_coord
            channel = 0 if self.air else 1
            if self.team == TEAM1_BACKGROUND:
                env[self.x, self.y] = TEAM1_UAV if self.air else TEAM1_UGV
            else:
                env[self.x, self.y] = TEAM2_UAV if self.air else TEAM2_UGV        
        else:
            print("error: wrong action selected")

    def individual_reward(self, env):
        """
        Generates reward for individual
        :param self:
        :return:
        """
        # Small reward range [-1, 1]
        lx, ly = self.get_loc()
        small_observation = [[-1 for i in range(2 * self.range + 1)] for j in range(2 * self.range + 1)]
        small_reward = 0
        if self.air:
            for x in range(lx - self.range, lx + self.range + 1):
                for y in range(ly - self.range, ly + self.range + 1):
                    if ((x - lx) ** 2 + (y - ly) ** 2 <= self.range ** 2) and \
                            0 <= x < self.map_size[0] and \
                            0 <= y < self.map_size[1]:
                        small_observation[x - lx + self.range][y - ly + self.range] = self._env[x][y]
                        # Max reward for finding red flag
                        if env[x][y] == TEAM2_FLAG:
                            small_reward = .5
                        # Reward for UAV finding enemy wherever
                        elif env[x][y] == TEAM2_UGV:
                            small_reward += .5 / NUM_RED
        else:
            if env[lx][ly] == TEAM2_FLAG:
                small_reward = 1
            elif not self.isAlive:
                small_reward = -1
        return small_reward

    def get_loc(self):
        return self.x, self.y

    def report_loc(self):
        print("report: position x:%d, y:%d" % (self.x, self.y))


class GroundVehicle(Agent):
    """This is a child class for ground agents. Inherited from Agent class.
    It creates an instance of UGV in specific location"""

    def __init__(self, loc, map_only, team_number):
        """
        Constructor

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        Agent.__init__(self, loc, map_only, team_number)


# noinspection PyCallByClass
class AerialVehicle(Agent):
    """This is a child class for aerial agents. Inherited from Agent class.
    It creates an instance of UAV in specific location"""

    def __init__(self, loc, map_only, team_number):
        """
        Constructor

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        Agent.__init__(self, loc, map_only, team_number)
        self.step = UAV_STEP
        self.range = UAV_RANGE
        self.a_range = UAV_A_RANGE
        self.air = True


class CivilAgent(GroundVehicle):
    """This is a child class for civil agents. Inherited from UGV class.
    It creates an instance of civil in specific location"""

    def __init__(self, loc, map_only, team_number):
        """
        Constructor

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        Agent.__init__(self, loc, map_only, team_number)
        self.direction = [0, 0]
        self.isDone = False
