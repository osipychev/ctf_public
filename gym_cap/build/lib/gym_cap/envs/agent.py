import numpy as np
#from gym import error, spaces, utils
#from gym.utils import seeding
#from .cap_view2d import CaptureView2D
from .const import *
#from .create_map import CreateMap
from .enemy_ai import EnemyAI

class Agent():
    """This is a parent class for all agents.
    It creates an instance of agent in specific location"""

    def __init__(self, loc, map_only):
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
        self.atHome = True
        self.x, self.y = loc
        self.step = UGV_STEP
        self.range = UGV_RANGE
        self.a_range = UGV_A_RANGE
        self.air = False
        self.ai = EnemyAI(map_only)

    def move(self, action):
        x, y = self.x, self.y
        if action == "X":
            pass
        elif action == "W":
            x -= self.step
        elif action == "E":
            x += self.step
        elif action == "N":
            y -= self.step
        elif action == "S":
            y += self.step
        else:
            print("error: wrong action selected")

        self.x = x#max(min(WORLD_W-1, x), 0)
        self.y = y#max(min(WORLD_H-1, y), 0)

    def get_loc(self):
        return self.x, self.y

    def report_loc(self):
        print("report: position x:%d, y:%d" % (self.x, self.y))

class GroundVehicle(Agent):
    """This is a child class for ground agents. Inherited from Ageng class.
    It creates an instance of UGV in specific location"""
    def __init__(self, loc, map_only):
        """
        Constructor

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        Agent.__init__(self, loc, map_only)

class AerialVehicle(Agent):
    """This is a child class for aerial agents. Inherited from Ageng class.
    It creates an instance of UAV in specific location"""
    def __init__(self, loc, map_only):
        """
        Constructor

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        Agent.__init__(self, loc, map_only)
        self.step = UAV_STEP
        self.range = UAV_RANGE
        self.a_range = UAV_A_RANGE
        self.air = True

class CivilAgent(GroundVehicle):
    """This is a child class for civil agents. Inherited from UGV class.
    It creates an instance of civil in specific location"""
    def __init__(self, loc, map_only):
        """
        Constructor

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        Agent.__init__(self, loc, map_only)
        self.direction = [0, 0]
        self.isDone = False
        # ! not used for now

#    def move():
#        if not self.isDone:
#            self.l
#
#    def check_complete(self):
#        return self.isDone