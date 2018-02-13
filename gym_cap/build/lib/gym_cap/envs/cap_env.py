#TODO create documentation
import numpy as np

import gym
import os
from gym import error, spaces, utils
from gym.utils import seeding
from .cap_view2d import CaptureView2D

from const import TeamConst, MapConst

TEAM1_BACKGROUND = 0
TEAM2_BACKGROUND = 1
TEAM1_ENTITY = 2
TEAM2_ENTITY = 3

class CapEnv(gym.Env):
    metadata = {
        "render.modes": ["fast", "human"],
    }

    ACTION = ["N", "E", "S", "W", "X"]

    def __init__(self, env_matrix_file=None, mode=None):

        #TODO check if exists
        # if mode=="":
            # self.cap_view = CaptureView2D(game_name="Capture The Flag Gym - (%s)" % \
                                          # env_matrix_file, environment_path=env_matrix_file)
        # else:
            # self.cap_view = CaptureView2D()

        self.matrix_file = env_matrix_file
        self.create_env(env_matrix_file)
        self.map_size = (len(self._env[0]), len(self._env))

        self.team1 = []
        self.team2 = []
        for row in range(len(self._env)):
            for col in range(len(self._env[0])):
                if self._env[row][col] == 2:
                    cur_ent = GroundVehicle((col, row))
                    self.team1.append(cur_ent)
                elif col == 3:
                    cur_ent = GroundVehicle((col, row))
                    self.team2.append(cur_ent)

        #TODO broken ACTION scope
        # self.action_space1 = [ACTION for i in range(len(self.team1))]
        # self.action_space2 = [ACTION for i in range(len(self.team2))]
        self.action_space = [["N", "E", "S", "W", "X"] for i in range(len(self.team1))]
        self.action_space2 = [["N", "E", "S", "W", "X"] for i in range(len(self.team2))]

        self.create_observation_space()
        self.state = self.observation_space
        self.cap_view = CaptureView2D()

        #TODO necessary?
        self._seed()

    #TODO
    def create_env(self, matrix_file):
        # dir_path = os.path.dirname(os.path.abspath(__file__))
        # rel_path = os.path.join(dir_path, "ctf_samples", matrix_file)
        rel_path = "/Users/Zach/Projects/Research-SP18/missionplanner/gym_cap/gym_cap/envs/ctf_samples/cap2d_000.npy"
        self._env = np.load(rel_path)

    #TODO
    def create_reward(self):
        pass

    def create_action_space(self, team):
        """
        Creates the action space in self.action_space

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        if team == 1:
            self.action_space = ["X" for i in range(len(team1))]
            for i in range(len(team1)):
                if team1[i].isAlive:
                    self.action_space[i] = ACTION
                    locx, locy = team1[i].get_loc()
                    if locx == 0:
                        self.action_space.remove("W")
                    elif locx == self.map_size[0]-1:
                        self.action_space.remove("E")
                    if locy == 0:
                        self.action_space.remove("N")
                    elif locy == self.map_size[1]-1:
                        self.action_space.remove("S")
        elif team == 2:
            self.action_space2 = ["X" for i in range(len(team2))]
            for i in range(len(team2)):
                if team2[i].isAlive:
                    self.action_space2[i] = ACTION
                    locx, locy = team2[i].get_loc()
                    if locx == 0:
                        self.action_space2.remove("W")
                    elif locx == self.map_size[0]-1:
                        self.action_space2.remove("E")
                    if locy == 0:
                        self.action_space2.remove("N")
                    elif locy == self.map_size[1]-1:
                        self.action_space2.remove("S")

    def create_observation_space(self):
        """
        Creates the observation space in self.observation_space

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        #Always returns team1
        self.observation_space = np.full((self.map_size[0], self.map_size[1]), -1)
        for agent in self.team1:
            loc = agent.get_loc()
            for xi in range(-agent.range, agent.range+1):
                for yi in range(-agent.range, agent.range+1):
                    locx, locy = loc[0] + xi, loc[1] + yi
                    if not (locx < 0 or locx >= self.map_size[0]) and \
                            not (locy < 0 or locy >= self.map_size[1]):
                        self.observation_space[locx][locy] = self._env[locx][locy]

    def move_entity(self, action, unit, team):
        if team == 1:
            locx, locy = self.team1[unit].get_loc()
            if action == "N":
                if self.team1[unit].atHome:
                    self._env[locx][locy] = TEAM1_BACKGROUND
                else:
                    self._env[locx][locy] = TEAM2_BACKGROUND
                self._env[locx][locy-1] = TEAM1_ENTITY
            elif action == "S":
                if self.team1[unit].atHome:
                    self._env[locx][locy] = TEAM1_BACKGROUND
                else:
                    self._env[locx][locy] = TEAM2_BACKGROUND
                self._env[locx][locy+1] = TEAM1_ENTITY
            elif action == "E":
                if self.team1[unit].atHome:
                    self._env[locx][locy] = TEAM1_BACKGROUND
                else:
                    self._env[locx][locy] = TEAM2_BACKGROUND
                self._env[locx-1][locy] = TEAM1_ENTITY
            elif action == "W":
                if self.team1[unit].atHome:
                    self._env[locx][locy] = TEAM1_BACKGROUND
                else:
                    self._env[locx][locy] = TEAM2_BACKGROUND
                self._env[locx+1][locy] = TEAM1_ENTITY
        elif team == 2:
            locx, locy = self.team2[unit].get_loc()
            if action == "N":
                if self.team2[unit].atHome:
                    self._env[locx][locy] = TEAM2_BACKGROUND
                else:
                    self._env[locx][locy] = TEAM1_BACKGROUND
                self._env[locx][locy-1] = TEAM2_ENTITY
            elif action == "S":
                if self.team2[unit].atHome:
                    self._env[locx][locy] = TEAM2_BACKGROUND
                else:
                    self._env[locx][locy] = TEAM1_BACKGROUND
                self._env[locx][locy+1] = TEAM2_ENTITY
            elif action == "E":
                if self.team2[unit].atHome:
                    self._env[locx][locy] = TEAM2_BACKGROUND
                else:
                    self._env[locx][locy] = TEAM1_BACKGROUND
                self._env[locx-1][locy] = TEAM2_ENTITY
            elif action == "W":
                if self.team2[unit].atHome:
                    self._env[locx][locy] = TEAM2_BACKGROUND
                else:
                    self._env[locx][locy] = TEAM1_BACKGROUND
                self._env[locx+1][locy] = TEAM2_ENTITY
        else:
            raise("Team number must be 1 or 2.")

    #TODO necessary?
    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, entities_action):
        """
        Takes one step in the cap the flag game

        Parameters
        ----------
        self    : object
            CapEnv object
        entities_action  : list
            contains actions for entity 1-n
        team  : int
            which team number is making an action

        Returns
        -------
        state    : object
            CapEnv object
        reward  : float
            float containing the reward for the given action
        isDone  : bool
            decides if the game is over
        info    :
            Not sure TODO
        """
        if isinstance(entities_action[0], int):
            for i in range(len(entities_action)):
                self.move_entity(self.ACTION[entities_action[i]], i, 1)
        else:
            for i in range(len(entities_action)):
                self.move_entity(entities_action[i], i, 1)

        #TODO
        #Get team2 actions from heuristic function
        # team2_actions = generate_actions()
        team2_actions = ["X"]*len(self.team2)

        #Move team2
        for i in range(len(team2_actions)):
            self.move_entity(team2_actions[i], i, 2)

        #TODO Reward statement
        # reward = create_reward()
        reward = 0

        self.create_observation_space()
        self.state = self.observation_space

        #TODO game over
        isDone = False
        info = {}

        return self.state, reward, isDone, info

    def _reset(self):
        """
        Resets the game

        Parameters
        ----------
        self    : object
            CapEnv object

        Returns
        -------
        state    : object
            CapEnv object
        """
        self.create_env(self.matrix_file)

        self.team1 = []
        self.team2 = []
        for row in range(len(self._env)):
            for col in range(len(self._env[0])):
                if self._env[row][col] == 2:
                    cur_ent = GroundVehicle((col, row))
                    self.team1.append(cur_ent)
                elif col == 3:
                    cur_ent = GroundVehicle((col, row))
                    self.team2.append(cur_ent)

        self.create_observation_space()
        self.state = self.observation_space

        return self.state

    #TODO
    def is_game_over(self):
        pass

    def _render(self, mode="human", close=False):
        if close:
            self.cap_view.quit_game()
        self.cap_view.update_env(self._env)
        return

class Agent():

    def __init__(self, loc):
        self.isAlive = True
        self.atHome = True
        self.x, self.y = loc
        self.step = TeamConst.UGV_STEP
        self.range = TeamConst.UGV_RANGE

    def move(self, action):
        x, y = self.x, self.y
        if action == 0:
            pass
        elif action == 1:
            x -= self.step
        elif action == 2:
            x += self.step
        elif action == 3:
            y -= self.step
        elif action == 4:
            y += self.step
        else:
            print("error: wrong action selected")

        self.x = max(min(MapConst.WORLD_W-1, x), 0)
        self.y = max(min(MapConst.WORLD_H-1, y), 0)

    def get_loc(self):
        return self.x, self.y

    def report_loc(self):
        print("report: position x:%d, y:%d" % (self.x, self.y))


class GroundVehicle(Agent):

    def __init__(self, loc):
        Agent.__init__(self, loc)


class AerialVehicle(Agent):

    def __init__(self, loc):
        Agent.__init__(self, loc)
        self.step = TeamConst.UAV_STEP
        self.range = TeamConst.UAV_RANGE


class GrayAgent(GroundVehicle):

    def __init__(self, loc):
        Agent.__init__(self, loc, TeamConst.GRAY)
        self.direction = [0, 0]
        # ! not used for now

    def check_complete(self):
        return self.get_loc == self.direction

#Different environment sizes
class CapEnvSample20x20(CapEnv):

    def __init__(self):
        super(CapEnvSample20x20, self).__init__(env_matrix_file="ctf_samples/cap2d_000.npy")

#DEBUGGING
# if __name__ == "__main__":
    # cap_env = CapEnv(env_matrix_file="ctf_samples/cap2d_000.npy")
