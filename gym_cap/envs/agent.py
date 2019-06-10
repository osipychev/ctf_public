# from gym import error, spaces, utils
# from gym.utils import seeding
# from .cap_view2d import CaptureView2D
from .const import *
import numpy as np
# from .create_map import CreateMap
#from .enemy_ai import EnemyAI
import math


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
        self.length, self.breath = map_only.shape
        self.step = UGV_STEP
        self.range = UGV_RANGE
        self.a_range = UGV_A_RANGE
        self.air = False
        self.memory = np.full((self.length, self.breath), -1)
        self.memory_mode = "None"
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
            if env[self.x][self.y] == DEAD:
                env[self.x][self.y] = team_home[self.x][self.y]   # agent replaced with home background after it dies
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
            if self.team == TEAM1_BACKGROUND:
                env[self.x, self.y] = TEAM1_UAV if self.air else TEAM1_UGV
            else:
                env[self.x, self.y] = TEAM2_UAV if self.air else TEAM2_UGV        
        else:
            print("error: wrong action selected")
    
    def update_memory(self, env):

        """
        saves/updates individual map of an agent

        """
        
        obs = self.get_obs(env = env)
        leng, breth = obs.shape
        l, b = leng//2, breth//2
        terrain = [TEAM1_FLAG, TEAM2_FLAG, OBSTACLE, TEAM1_BACKGROUND, TEAM2_BACKGROUND]
        loc_x, loc_y = self.get_loc()
             
        coord_x, coord_y = np.where(np.isin(obs, terrain))
        offset = np.array([(l - loc_x), (b - loc_y)])
        offset_x, offset_y = offset
        coord_x = coord_x[np.logical_and(coord_x >= offset_x, coord_x < self.length + offset_x)]
        coord_y = coord_y[np.logical_and(coord_y >= offset_y, coord_y < self.breath + offset_y)]
        for coord in zip(coord_x, coord_y):
            self.memory[coord - offset] = obs[coord]

        return self.memory
    
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

    def get_obs(self, env, com_ground=False, com_air=False, distance=None, freq=1.0, *args):
        if self.team == BLUE:
            myTeam = env.get_team_blue
        else:
            myTeam = env.get_team_red

        a = 39              # env.map_size[0]*2-1
        b = 39              # env.map_size[1]*2-1
        obs = np.full(shape=(a, b), fill_value=UNKNOWN)
        val = env.get_full_state

        if not self.isAlive:        # if target agent is dead, return all -1
            return obs

        loc = self.get_loc()
        x, y = loc[0], loc[1]
        for i in range(-self.range, self.range + 1):
            for j in range(-self.range, self.range + 1):
                locx, locy = i + loc[0], j + loc[1]
                if (i * i + j * j <= self.range ** 2) and \
                        not (locx < 0 or locx > env.map_size[0] - 1) and \
                        not (locy < 0 or locy > env.map_size[1] - 1):
                    obs[locx+int(a/2)-loc[0]][locy+int(b/2)-loc[1]] = val[locx][locy]
                else:
                    obs[locx + int(a/2) - loc[0]][locy + int(b/2) - loc[1]] = OBSTACLE

        def distance_list(location, agents, distance):
            List = []
            for agent in agents:
                loc = agent.get_loc()
                dist = math.hypot(loc[0] - location[0], loc[1] - location[1])
                if dist < distance:
                    List.append(agent)
            return List

        if distance is not None:
            myTeam = distance_list(loc, myTeam, distance)

        if not com_ground and not com_air:
            return obs

        for agent in myTeam:
            if not agent.isAlive:
                continue
            if not com_air and agent.air:
                continue
            elif com_air and agent.air:
                loc = agent.get_loc()

                for i in range(-self.range, self.range + 1):
                    for j in range(-self.range, self.range + 1):
                        locx, locy = i + loc[0], j + loc[1]
                        if (i * i + j * j <= self.range ** 2) and \
                                not (locx < 0 or locx > env.map_size[0] - 1) and \
                                not (locy < 0 or locy > env.map_size[1] - 1):
                            obs[locx + int(a / 2) - x][locy + int(b / 2) - y] = val[locx][locy]
                        else:
                            obs[locx + int(a / 2) - x][locy + int(b / 2) - y] = OBSTACLE

                        if freq is not None and np.random.random() > freq:
                            obs[locx + int(a / 2) - x][locy + int(b / 2) - y] = UNKNOWN

            elif not com_ground and not agent.air:
                continue
            elif com_ground and not agent.air:
                loc = agent.get_loc()
                for i in range(-self.range, self.range + 1):
                    for j in range(-self.range, self.range + 1):
                        locx, locy = i + loc[0], j + loc[1]
                        if (i * i + j * j <= self.range ** 2) and \
                                not (locx < 0 or locx > env.map_size[0] - 1) and \
                                not (locy < 0 or locy > env.map_size[1] - 1):
                            obs[locx + int(a / 2) - x][locy + int(b / 2) - y] = val[locx][locy]
                        else:
                            obs[locx + int(a / 2) - x][locy + int(b / 2) - y] = OBSTACLE

                        if freq is not None and np.random.random() > freq:
                            obs[locx + int(a / 2) - x][locy + int(b / 2) - y] = UNKNOWN

        return obs

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
