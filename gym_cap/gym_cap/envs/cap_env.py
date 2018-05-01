#TODO create documentation
import numpy as np

import gym
import os
<<<<<<< HEAD
=======
import sys
import random
>>>>>>> e958814... qol changes. reset in init, prepend ground units
from gym import error, spaces, utils
from gym.utils import seeding
from .cap_view2d import CaptureView2D
from .const import *
from .create_map import CreateMap
from .enemy_ai import EnemyAI
from .agent import *

from pandas import *


"""
Requires that all units initially exist in home zone.
"""
class CapEnv(gym.Env):
    metadata = {
        "render.modes": ["fast", "human"],
    }

    ACTION = ["N", "E", "S", "W", "X"]

    def __init__(self, map_size=20):
        """
        Constructor

        Parameters
        ----------
        self    : object
            CapEnv object
        """
<<<<<<< HEAD

        self._env = CreateMap.gen_map('map', map_size)
        self.map_size = (len(self._env), len(self._env[0]))
        self.team_home = self._env.copy()

        self.team1 = []
        self.team2 = []
        for x in range(len(self._env)):
            for y in range(len(self._env[0])):
                if self._env[x][y] == TEAM1_UGV:
                    cur_ent = GroundVehicle((x, y), self.team_home, 1)
                    self.team1.append(cur_ent)
                    self.team_home[x][y] = TEAM1_BACKGROUND
                elif self._env[x][y] == TEAM1_UAV:
                    cur_ent = AerialVehicle((x, y), self.team_home, 1)
                    self.team1.append(cur_ent)
                    self.team_home[x][y] = TEAM1_BACKGROUND
                elif self._env[x][y] == TEAM2_UGV:
                    cur_ent = GroundVehicle((x, y), self.team_home, 2)
                    self.team2.append(cur_ent)
                    self.team_home[x][y] = TEAM2_BACKGROUND
                elif self._env[x][y] == TEAM2_UAV:
                    cur_ent = AerialVehicle((x, y), self.team_home, 2)
                    self.team2.append(cur_ent)
                    self.team_home[x][y] = TEAM2_BACKGROUND

        #place arial units at end of list
        for i in range(len(self.team1)):
            if self.team1[i].air:
                self.team1.insert(len(self.team1)-1, self.team1.pop(i))
        for i in range(len(self.team2)):
            if self.team2[i].air:
                self.team2.insert(len(self.team2)-1, self.team2.pop(i))
        self.action_space = spaces.Box(0, len(self.ACTION)-1,\
                                       shape=(len(self.team1),), dtype=int)

        self.create_observation_space(RED)
        self.create_observation_space(BLUE)
        self.state = self.observation_space
        self.cap_view = CaptureView2D(screen_size=(600, 600))
        self.game_lost = False
        self.game_won = False
        self.cur_step = 0

        #Necessary for human mode
        self.first = True

        self._seed()
=======
        self._reset(map_size)
>>>>>>> e958814... qol changes. reset in init, prepend ground units

    def create_reward(self):
        """
        Range (-1, 1)

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        reward = 0
        #Win and loss return max rewards
        if self.game_lost:
            return -1
        if self.game_won:
            return 1

        #Dead enemy team gives .5/total units for each dead unit
        for i in self.team2:
            if not i.isAlive:
                reward+=(.5/len(self.team2))
        for i in self.team1:
            if not i.isAlive:
                reward-=(.5/len(self.team1))

        #10,000 steps returns -.5
        if self.cur_step > 10000:
            reward-=.5
        else:
            reward-=((self.cur_step/10000.0)*.5)

        return reward

    def create_observation_space(self, team=BLUE):
        """
        Creates the observation space in self.observation_space

        Parameters
        ----------
        self    : object
            CapEnv object
        """

        if team == BLUE:
            self.observation_space = np.full((self.map_size[0], self.map_size[1]), -1)
            for agent in self.team1:
                if not agent.isAlive:
                    continue
                loc = agent.get_loc()
                for i in range(-agent.range, agent.range + 1):
                    for j in range(-agent.range, agent.range + 1):
                        locx, locy = i + loc[0], j + loc[1]
                        if (i*i + j*j <= agent.range**2) and \
                            not (locx < 0 or locx > self.map_size[0]-1) and \
                            not (locy < 0 or locy > self.map_size[1]-1):
                            self.observation_space[locx][locy] = self._env[locx][locy]
        elif team == RED:
            self.observation_space2 = np.full((self.map_size[0], self.map_size[1]), -1)
            for agent in self.team2:
                if not agent.isAlive:
                    continue
                loc = agent.get_loc()
                for i in range(-agent.range, agent.range + 1):
                    for j in range(-agent.range, agent.range + 1):
                        locx, locy = i + loc[0], j + loc[1]
                        if (i*i + j*j <= agent.range**2) and \
                            not (locx < 0 or locx > self.map_size[0]-1) and \
                            not (locy < 0 or locy > self.map_size[1]-1):
                            self.observation_space2[locx][locy] = self._env[locx][locy]

    #TODO improve
    #Change from range to attack range
    def check_dead(self, entity_num, team):
        """
        Checks if a unit is dead

        Parameters
        ----------
        self    : object
            CapEnv object
        entity_num  : int
            Represents where in the unit list is the unit to move
        team    : int
            Represents which team the unit belongs to
        """
        if team == 1:
            loc = self.team1[entity_num].get_loc()
            cur_range = self.team1[entity_num].a_range
            for x in range(-cur_range, cur_range+1):
                for y in range(-cur_range, cur_range+1):
                    locx, locy = x + loc[0], y + loc[1]
                    if (x*x + y*y <= cur_range**2) and \
                        not (locx < 0 or locx > self.map_size[0]-1) and \
                        not (locy < 0 or locy > self.map_size[1]-1):
                        if self._env[locx][locy] == TEAM2_UGV:
                            if self.team_home[locx][locy] == TEAM1_BACKGROUND:
                                for i in range(len(self.team2)):
                                    enemy_locx, enemy_locy = self.team2[i].get_loc()
                                    if enemy_locx == locx and enemy_locy == locy:
                                        self.team2[i].isAlive = False
                                        self._env[locx][locy] = DEAD
                                        break
        elif team == 2:
            loc = self.team2[entity_num].get_loc()
            cur_range = self.team2[entity_num].a_range
            for x in range(-cur_range, cur_range+1):
                for y in range(-cur_range, cur_range+1):
                    locx, locy = x + loc[0], y + loc[1]
                    if (x*x + y*y <= cur_range**2) and \
                        not (locx < 0 or locx > self.map_size[0]-1) and \
                        not (locy < 0 or locy > self.map_size[1]-1):
                        if self._env[locx][locy] == TEAM1_UGV:
                            if self.team_home[locx][locy] == TEAM2_BACKGROUND:
                                for i in range(len(self.team1)):
                                    enemy_locx, enemy_locy = self.team1[i].get_loc()
                                    if enemy_locx == locx and enemy_locy == locy:
                                        self.team1[i].isAlive = False
                                        self._env[locx][locy] = DEAD
                                        break


    #TODO necessary?
    def _seed(self, seed=None):
        """
        todo docs still

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, entities_action, mode="sandbox"):
        """
        Takes one step in the cap the flag game

        Parameters
        ----------
        self    : object
            CapEnv object
        entities_action  : list
            contains actions for entity 1-n

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
        # print(DataFrame(self._env))
        self.cur_step+=1
<<<<<<< HEAD
=======
        move_list = []
        for i in range(NUM_BLUE+NUM_UAV):
            move_list.append(entities_action%5)
            entities_action = int(entities_action/5)
        #ERROR checking
        if not len(move_list) == NUM_BLUE+NUM_UAV:
            sys.exit("You entered", len(move_list), "moves. There are", NUM_BLUE+NUM_UAV, "entities.")

>>>>>>> e958814... qol changes. reset in init, prepend ground units
        for i in range(len(self.team1)):
            self.team1[i].move(self.ACTION[entities_action[i]], self._env, self.team_home)

        #TODO
        #Get team2 actions from heuristic function
        # team2_actions = generate_actions()

        #Move team2
        if mode=="run_away":
            team2_actions = generate_run_actions()
        elif mode=="random":
            team2_actions = self.action_space.sample()
        elif mode=="defend":
            team2_actions = EnemyAI.patrol(self.team2)
        elif mode=="attack":
            team2_actions = self.action_space.sample()
        elif mode=="sandbox":
            for i in range(len(self.team2)):
                locx, locy = self.team2[i].get_loc()
                if self.team2[i].atHome:
                    self._env[locx][locy] = TEAM2_BACKGROUND
                else:
                    self._env[locx][locy] = TEAM1_BACKGROUND
            self.team2=[]
        elif mode=="patrol":
            team2_actions = []
            for agent in self.team2:
                team2_actions.append(agent.ai.patrol(agent, self.observation_space2, self.team2))
        elif mode=="random":
            team2_actions = self.action_space.sample()  # choose random action
        elif mode=="human":
            self._render("env")
            team2_actions = self.cap_view.human_move(self._env, self.team2)

        for i in range(len(self.team2)):
            self.team2[i].move(self.ACTION[team2_actions[i]], self._env, self.team_home)

        #Check for dead
        for i in range(len(self.team1)):
            if not self.team1[i].atHome or self.team1[i].air or not self.team1[i].isAlive:
                continue
            self.check_dead(i, 1)
        for i in range(len(self.team2)):
            if not self.team2[i].atHome or self.team2[i].air or not self.team2[i].isAlive:
                continue
            self.check_dead(i, 2)

        #Check win and lose conditions
        has_alive_entity = False
        for i in self.team2:
            if i.isAlive and not i.air:
                has_alive_entity = True
                locx, locy = i.get_loc()
                if self.team_home[locx][locy] == TEAM1_FLAG:
                    self.game_lost = True

        if not has_alive_entity and mode!="sandbox":
            self.game_won = True
            self.game_lost = False
        has_alive_entity = False
        for i in self.team1:
            if i.isAlive and not i.air:
                has_alive_entity = True
                locx, locy = i.get_loc()
                if self.team_home[locx][locy] == TEAM2_FLAG:
                    self.game_lost = False
                    self.game_won = True
        if not has_alive_entity:
            self.game_lost = True
            self.game_won = False

        reward = self.create_reward()

        self.create_observation_space(BLUE)
        self.create_observation_space(RED)
        self.state = self.observation_space

        #TODO game over
        isDone = False
        if self.game_won or self.game_lost:
            isDone = True
        info = {}
        if self.game_won:
            print("YOU'RE A WINNER!")
        if self.game_lost:
            print("YOU'RE A LOSER!")

        return self.state, reward, isDone, info

    def _reset(self, map_size=None, in_seed=None):
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
<<<<<<< HEAD
        self._env = CreateMap.gen_map('map', dim=self.map_size[0], in_seed=in_seed)
=======

        if map_size == None:
            self._env = CreateMap.gen_map('map', dim=self.map_size[0], in_seed=4)
        else:
            self._env = CreateMap.gen_map('map', map_size)

        self.map_size = (len(self._env), len(self._env[0]))
>>>>>>> e958814... qol changes. reset in init, prepend ground units
        self.team_home = self._env.copy()

        self.team1 = []
        self.team2 = []
        for y in range(len(self._env)):
            for x in range(len(self._env[0])):
                if self._env[x][y] == TEAM1_UGV:
                    cur_ent = GroundVehicle((x, y), self.team_home, 1)
                    self.team1.insert(0, cur_ent)
                    self.team_home[x][y] = TEAM1_BACKGROUND
                elif self._env[x][y] == TEAM1_UAV:
                    cur_ent = AerialVehicle((x, y), self.team_home, 1)
                    self.team1.append(cur_ent)
                    self.team_home[x][y] = TEAM1_BACKGROUND
                elif self._env[x][y] == TEAM2_UGV:
                    cur_ent = GroundVehicle((x, y), self.team_home, 2)
                    self.team2.insert(0, cur_ent)
                    self.team_home[x][y] = TEAM2_BACKGROUND
                elif self._env[x][y] == TEAM2_UAV:
                    cur_ent = AerialVehicle((x, y), self.team_home, 2)
                    self.team2.append(cur_ent)
                    self.team_home[x][y] = TEAM2_BACKGROUND

        for i in self.team2:
            print(i.air)
        # print(DataFrame(self._env))
        #place arial units at end of list
        for i in range(len(self.team1)):
            if self.team1[i].air:
                self.team1.insert(len(self.team1), self.team1.pop(i))
        for i in range(len(self.team2)):
            if self.team2[i].air:
                self.team2.insert(len(self.team2)-1, self.team2.pop(i))

        self.action_space = spaces.Discrete(len(self.ACTION)**(NUM_BLUE+NUM_UAV))

        self.game_lost = False
        self.game_won = False

        self.create_observation_space(RED)
        self.create_observation_space(BLUE)
        self.state = self.observation_space
        self.cap_view = CaptureView2D(screen_size=(800, 800))
        self.viewer = None

        self.game_lost = False
        self.game_won = False
        self.cur_step = 0

        #Necessary for human mode
        self.first = True

        self._seed()

        return self.state

    def _render(self, mode="obs", close=False):
        """
        Renders the screen options="obs, env"

        Parameters
        ----------
        self    : object
            CapEnv object
        mode    : string
            Defines what will be rendered
        """
        if close:
            self.cap_view.quit_game()
        if mode=="env":
            self.cap_view.update_env(self._env)
        elif mode=="obs":
            self.cap_view.update_env(self.observation_space)
        elif mode=="obs2":
            self.cap_view.update_env(self.observation_space2)
        elif mode=="team":
            self.cap_view.update_env(self.team_home)
        return



#Different environment sizes
class CapEnvGenerate20x20(CapEnv):
    def __init__(self):
        super(CapEnvGenerate20x20, self).__init__(map_size=20)

class CapEnvGenerate100x100(CapEnv):
    def __init__(self):
        super(CapEnvGenerate100x100, self).__init__(map_size=100)

class CapEnvGenerate500x500(CapEnv):
    def __init__(self):
        super(CapEnvGenerate500x500, self).__init__(map_size=500)


#DEBUGGING
# if __name__ == "__main__":
    # cap_env = CapEnv(env_matrix_file="ctf_samples/cap2d_000.npy")
