#TODO create documentation
import numpy as np

import gym
import os
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

        self._env = CreateMap.gen_map('map', map_size)
        self.map_size = (len(self._env[0]), len(self._env))
        self.team_home = self._env.copy()

        self.team1 = []
        self.team2 = []
        for row in range(len(self._env)):
            for col in range(len(self._env[0])):
                if self._env[row][col] == TEAM1_UGV:
                    cur_ent = GroundVehicle(loc=(col, row),map_only=self.team_home)
                    self.team1.append(cur_ent)
                    self.team_home[row][col] = TEAM1_BACKGROUND
                elif self._env[row][col] == TEAM1_UAV:
                    cur_ent = AerialVehicle(loc=(col, row),map_only=self.team_home)
                    self.team1.append(cur_ent)
                    self.team_home[row][col] = TEAM1_BACKGROUND
                elif self._env[row][col] == TEAM2_UGV:
                    cur_ent = GroundVehicle(loc=(col, row),map_only=self.team_home)
                    self.team2.append(cur_ent)
                    self.team_home[row][col] = TEAM2_BACKGROUND
                elif self._env[row][col] == TEAM2_UAV:
                    cur_ent = AerialVehicle(loc=(col, row),map_only=self.team_home)
                    self.team2.append(cur_ent)
                    self.team_home[row][col] = TEAM2_BACKGROUND

        # print(DataFrame(self.team_home))
        # print(DataFrame(self._env))
        # self.action_space = spaces.discrete(0, len(self.ACTION)-1,\
                                       # shape=(len(self.team1),), dtype=int)
        self.action_space = spaces.Discrete(len(self.ACTION)**(NUM_BLUE+NUM_UAV))

        self.create_observation_space(RED)
        self.create_observation_space(BLUE)
        self.state = self.observation_space
        self.cap_view = CaptureView2D(screen_size=(800, 800))
        self.game_lost = False
        self.game_won = False
        self.cur_step = 0

        #TODO necessary?
        self._seed()

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
        # if self.game_lost:
            # return -1
        # if self.game_won:
            # return 1

        #Dead enemy team gives .5/total units for each dead unit
        for i in self.team2:
            if not i.isAlive:
                reward+=(.5/len(self.team2))
        for i in self.team1:
            if not i.isAlive:
                reward-=(.5/len(self.team1))

        #10,000 steps returns -.5
        # map_size_2 = map_size[0]*map_size[1]
        # reward-=(.5/map_size_2)
        reward-=(.5/100)
        if self.game_won:
            reward+=1
        if reward <= -1:
            reward = -1
            self.game_lost = True
        # if self.cur_step > 10000:
            # reward-=.5
        # else:
            # reward-=((self.cur_step/10000.0)*.5)

        return reward

    def create_observation_space(self, team=BLUE):
        """
        Creates the observation space in self.observation_space

        Parameters
        ----------
        self    : object
            CapEnv object
        """

        #Always returns team1
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
                            self.observation_space[locy][locx] = self._env[locy][locx]
#                for i in range(agent.range+1):
#                    locx, locy = loc[0] + i, loc[1] + (agent.range-i)
#                    neg_locx = loc[0] - i
#                    neg_locy = loc[1] - (agent.range-i)
#                    for j in range(neg_locy, locy+1):
#                        if locx < self.map_size[0]:
#                            if  j < self.map_size[1] and j >= 0:
#                                self.observation_space[j][locx] = self._env[j][locx]
#                        if neg_locx >= 0:
#                            if  j < self.map_size[1] and j >= 0:
#                                self.observation_space[j][neg_locx] = self._env[j][neg_locx]

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
                            self.observation_space2[locy][locx] = self._env[locy][locx]
#                for xi in range(-agent.range, agent.range+1):
#                    for yi in range(-agent.range, agent.range+1):
#                        locx, locy = loc[0] + xi, loc[1] + yi
#                        if not (locx < 0 or locx > self.map_size[0]-1) and \
#                                not (locy < 0 or locy > self.map_size[1]-1):
#                            self.observation_space2[locy][locx] = self._env[locy][locx]


    def move_entity(self, action, unit, team):
        """
        Moves each unit individually. Checks if action is valid first.
        Also checks if game is over (enemy unit touches flag)

        Parameters
        ----------
        self    : object
            CapEnv object
        action  : string
            Action the unit is to take
        unit    : int
            Represents where in the unit list is the unit to move
        team    : int
            Represents which team the unit belongs to
        """
        if team == 1:
            if not self.team1[unit].isAlive:
                return
            locx, locy = self.team1[unit].get_loc()
            unit_step = self.team1[unit].step
            if action == "N":
                if locy-unit_step >= 0 \
                        and self._env[locy-unit_step][locx]!=OBSTACLE \
                        and self._env[locy-unit_step][locx]!=TEAM1_UGV \
                        and self._env[locy-unit_step][locx]!=TEAM2_UGV \
                        and self._env[locy-unit_step][locx]!=TEAM1_UAV \
                        and self._env[locy-unit_step][locx]!=TEAM2_UAV \
                        and self._env[locy-unit_step][locx]!=TEAM1_FLAG:
                    if self._env[locy-unit_step][locx]==TEAM2_FLAG:
                        if self.team1[unit].air:
                            return
                        self.game_won = True
                    self.team1[unit].move(action)
                    self._env[locy][locx] = self.team_home[locy][locx]
                    locx, locy = self.team1[unit].get_loc()
                    if self.team_home[locy][locx] == TEAM1_BACKGROUND or \
                            self.team_home[locy][locx] == TEAM1_FLAG:
                        self.team1[unit].atHome = True
                    if self.team1[unit].air:
                        self._env[locy][locx] = TEAM1_UAV
                    else:
                        self._env[locy][locx] = TEAM1_UGV
            elif action == "S":
                if locy+unit_step < self.map_size[1] \
                        and self._env[locy+unit_step][locx]!=OBSTACLE \
                        and self._env[locy+unit_step][locx]!=TEAM1_UGV \
                        and self._env[locy+unit_step][locx]!=TEAM2_UGV \
                        and self._env[locy-unit_step][locx]!=TEAM1_UAV \
                        and self._env[locy-unit_step][locx]!=TEAM2_UAV \
                        and self._env[locy+unit_step][locx]!=TEAM1_FLAG:
                    if self._env[locy+unit_step][locx]==TEAM2_FLAG:
                        if self.team1[unit].air:
                            return
                        self.game_won = True
                    self.team1[unit].move(action)
                    self._env[locy][locx] = self.team_home[locy][locx]
                    locx, locy = self.team1[unit].get_loc()
                    if self.team_home[locy][locx] == TEAM1_BACKGROUND or \
                            self.team_home[locy][locx] == TEAM1_FLAG:
                        self.team1[unit].atHome = True
                    if self.team1[unit].air:
                        self._env[locy][locx] = TEAM1_UAV
                    else:
                        self._env[locy][locx] = TEAM1_UGV
            elif action == "E":
                if locx+unit_step < self.map_size[0] \
                        and self._env[locy][locx+unit_step]!=OBSTACLE \
                        and self._env[locy][locx+unit_step]!=TEAM1_UGV \
                        and self._env[locy][locx+unit_step]!=TEAM2_UGV \
                        and self._env[locy-unit_step][locx]!=TEAM1_UAV \
                        and self._env[locy-unit_step][locx]!=TEAM2_UAV \
                        and self._env[locy][locx+unit_step]!=TEAM1_FLAG:
                    if self._env[locy][locx+unit_step]==TEAM2_FLAG:
                        if self.team1[unit].air:
                            return
                        self.game_won = True
                    self.team1[unit].move(action)
                    self._env[locy][locx] = self.team_home[locy][locx]
                    locx, locy = self.team1[unit].get_loc()
                    if self.team_home[locy][locx] == TEAM1_BACKGROUND or \
                            self.team_home[locy][locx] == TEAM1_FLAG:
                        self.team1[unit].atHome = True
                    if self.team1[unit].air:
                        self._env[locy][locx] = TEAM1_UAV
                    else:
                        self._env[locy][locx] = TEAM1_UGV
            elif action == "W":
                if locx-unit_step >= 0 \
                        and self._env[locy][locx-unit_step]!=OBSTACLE \
                        and self._env[locy][locx-unit_step]!=TEAM1_UGV \
                        and self._env[locy][locx-unit_step]!=TEAM2_UGV \
                        and self._env[locy-unit_step][locx]!=TEAM1_UAV \
                        and self._env[locy-unit_step][locx]!=TEAM2_UAV \
                        and self._env[locy][locx-unit_step]!=TEAM1_FLAG:
                    if self._env[locy][locx-unit_step]==TEAM2_FLAG:
                        if self.team1[unit].air:
                            return
                        self.game_won = True
                    self.team1[unit].move(action)
                    self._env[locy][locx] = self.team_home[locy][locx]
                    locx, locy = self.team1[unit].get_loc()
                    if self.team_home[locy][locx] == TEAM1_BACKGROUND or \
                            self.team_home[locy][locx] == TEAM1_FLAG:
                        self.team1[unit].atHome = True
                    if self.team1[unit].air:
                        self._env[locy][locx] = TEAM1_UAV
                    else:
                        self._env[locy][locx] = TEAM1_UGV
        elif team == 2:
            if not self.team2[unit].isAlive:
                return
            locx, locy = self.team2[unit].get_loc()
            unit_step = self.team2[unit].step
            if action == "N":
                if locy-unit_step >= 0 \
                        and self._env[locy-unit_step][locx]!=OBSTACLE \
                        and self._env[locy-unit_step][locx]!=TEAM1_UGV \
                        and self._env[locy-unit_step][locx]!=TEAM2_UGV \
                        and self._env[locy-unit_step][locx]!=TEAM1_UAV \
                        and self._env[locy-unit_step][locx]!=TEAM2_UAV \
                        and self._env[locy-unit_step][locx]!=TEAM2_FLAG:
                    if self._env[locy-unit_step][locx]==TEAM1_FLAG:
                        if self.team2[unit].air:
                            return
                        self.game_lost = True
                    self.team2[unit].move(action)
                    self._env[locy][locx] = self.team_home[locy][locx]
                    locx, locy = self.team2[unit].get_loc()
                    if self.team_home[locy][locx] == TEAM2_BACKGROUND or \
                            self.team_home[locy][locx] == TEAM2_FLAG:
                        self.team2[unit].atHome = True
                    if self.team2[unit].air:
                        self._env[locy][locx] = TEAM2_UAV
                    else:
                        self._env[locy][locx] = TEAM2_UGV
            elif action == "S":
                if locy+unit_step < self.map_size[1] \
                        and self._env[locy+unit_step][locx]!=OBSTACLE \
                        and self._env[locy+unit_step][locx]!=TEAM1_UGV \
                        and self._env[locy+unit_step][locx]!=TEAM2_UGV \
                        and self._env[locy-unit_step][locx]!=TEAM1_UAV \
                        and self._env[locy-unit_step][locx]!=TEAM2_UAV \
                        and self._env[locy+unit_step][locx]!=TEAM2_FLAG:
                    if self._env[locy+unit_step][locx]==TEAM1_FLAG:
                        if self.team2[unit].air:
                            return
                        self.game_lost = True
                    self.team2[unit].move(action)
                    self._env[locy][locx] = self.team_home[locy][locx]
                    locx, locy = self.team2[unit].get_loc()
                    if self.team_home[locy][locx] == TEAM2_BACKGROUND or \
                            self.team_home[locy][locx] == TEAM2_FLAG:
                        self.team2[unit].atHome = True
                    if self.team2[unit].air:
                        self._env[locy][locx] = TEAM2_UAV
                    else:
                        self._env[locy][locx] = TEAM2_UGV
            elif action == "E":
                if locx+unit_step < self.map_size[0] \
                        and self._env[locy][locx+unit_step]!=OBSTACLE \
                        and self._env[locy][locx+unit_step]!=TEAM1_UGV \
                        and self._env[locy][locx+unit_step]!=TEAM2_UGV \
                        and self._env[locy-unit_step][locx]!=TEAM1_UAV \
                        and self._env[locy-unit_step][locx]!=TEAM2_UAV \
                        and self._env[locy][locx+unit_step]!=TEAM2_FLAG:
                    if self._env[locy][locx+unit_step]==TEAM1_FLAG:
                        if self.team2[unit].air:
                            return
                        self.game_lost = True
                    self.team2[unit].move(action)
                    self._env[locy][locx] = self.team_home[locy][locx]
                    locx, locy = self.team2[unit].get_loc()
                    if self.team_home[locy][locx] == TEAM2_BACKGROUND or \
                            self.team_home[locy][locx] == TEAM2_FLAG:
                        self.team2[unit].atHome = True
                    if self.team2[unit].air:
                        self._env[locy][locx] = TEAM2_UAV
                    else:
                        self._env[locy][locx] = TEAM2_UGV
            elif action == "W":
                if locx-unit_step >= 0 \
                        and self._env[locy][locx-unit_step]!=OBSTACLE \
                        and self._env[locy][locx-unit_step]!=TEAM1_UGV \
                        and self._env[locy][locx-unit_step]!=TEAM2_UGV \
                        and self._env[locy-unit_step][locx]!=TEAM1_UAV \
                        and self._env[locy-unit_step][locx]!=TEAM2_UAV \
                        and self._env[locy][locx-unit_step]!=TEAM2_FLAG:
                    if self._env[locy][locx-unit_step]==TEAM1_FLAG:
                        if self.team2[unit].air:
                            return
                        self.game_lost = True
                    self.team2[unit].move(action)
                    self._env[locy][locx] = self.team_home[locy][locx]
                    locx, locy = self.team2[unit].get_loc()
                    if self.team_home[locy][locx] == TEAM2_BACKGROUND or \
                            self.team_home[locy][locx] == TEAM2_FLAG:
                        self.team2[unit].atHome = True
                    if self.team2[unit].air:
                        self._env[locy][locx] = TEAM2_UAV
                    else:
                        self._env[locy][locx] = TEAM2_UGV
        else:
            raise("Team number must be 1 or 2.")

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
                        if self._env[locy][locx] == TEAM2_UGV:
                            if self.team_home[locy][locx] == TEAM1_BACKGROUND:
                                for i in range(len(self.team2)):
                                    enemy_locx, enemy_locy = self.team2[i].get_loc()
                                    if enemy_locx == locx and enemy_locy == locy:
                                        self.team2[i].isAlive = False
                                        self._env[locy][locx] = DEAD
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
                        if self._env[locy][locx] == TEAM1_UGV:
                            if self.team_home[locy][locx] == TEAM2_BACKGROUND:
                                for i in range(len(self.team1)):
                                    enemy_locx, enemy_locy = self.team1[i].get_loc()
                                    # print(enemy_locx, enemy_locy, locx+x, locy+y)
                                    if enemy_locx == locx and enemy_locy == locy:
                                        self.team1[i].isAlive = False
                                        self._env[locy][locx] = DEAD
                                        break


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

    def _step(self, entities_action):
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
        mode="sandbox"
        #DEBUGGING
        # print(DataFrame(self._env))
        self.cur_step+=1
        move_list = []
        for i in range(NUM_BLUE+NUM_UAV):
            move_list.append(entities_action%5)
            entities_action = int(entities_action/5)
        for i in range(len(move_list)):
            self.move_entity(self.ACTION[move_list[i]], i, 1)

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
                    self._env[locy][locx] = TEAM2_BACKGROUND
                else:
                    self._env[locy][locx] = TEAM1_BACKGROUND
            self.team2=[]
        elif mode=="patrol":
            team2_actions = []
            for agent in self.team2:
                team2_actions.append(agent.ai.patrol(agent, self.observation_space2, self.team2))
        elif mode=="random":
            team2_actions = self.action_space.sample()  # choose random action

        for i in range(len(self.team2)):
            self.move_entity(self.ACTION[team2_actions[i]], i, 2)


        for i in range(len(self.team2)):
            self.move_entity(self.ACTION[team2_actions[i]], i, 2)

        #Check for dead
        for i in range(len(self.team1)):
            if not self.team1[i].atHome or self.team1[i].air or not self.team1[i].isAlive:
                continue
            self.check_dead(i, 1)

        for i in range(len(self.team2)):
            if not self.team2[i].atHome or self.team2[i].air or not self.team2[i].isAlive:
                continue
            self.check_dead(i, 2)

        has_alive_entity = False
        for i in self.team2:
            if i.isAlive and not i.air:
                has_alive_entity = True
                break
        if not has_alive_entity and mode!="sandbox":
            self.game_won = True

        has_alive_entity = False
        for i in self.team1:
            if i.isAlive and not i.air:
                has_alive_entity = True
                break

        if not has_alive_entity:
            self.game_lost = True

        reward = self.create_reward()
        if reward <= -1:
            reward = -1
            game_lost = True

        # self.create_observation_space(BLUE)
        # self.create_observation_space(RED)
        # self.state = self.observation_space
        self.state = self._env

        #TODO game over
        isDone = False
        if self.game_won or self.game_lost:
            isDone = True
        info = {}
        # if self.game_won:
            # print("YOU'RE A WINNER!")
        # if self.game_lost:
            # print("YOU'RE A LOSER!")


        return self.state, reward, isDone, info

    def _reset(self, in_seed=None):
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

        self._env = CreateMap.gen_map('map', dim=self.map_size[0], in_seed=1)
        self.team_home = self._env.copy()

        self.team1 = []
        self.team2 = []
        for row in range(len(self._env)):
            for col in range(len(self._env[0])):
                if self._env[row][col] == TEAM1_UGV:
                    cur_ent = GroundVehicle(loc=(col, row),map_only=self.team_home)
                    self.team1.append(cur_ent)
                    self.team_home[row][col] = TEAM1_BACKGROUND
                elif self._env[row][col] == TEAM1_UAV:
                    cur_ent = AerialVehicle(loc=(col, row),map_only=self.team_home)
                    self.team1.append(cur_ent)
                    self.team_home[row][col] = TEAM1_BACKGROUND
                elif self._env[row][col] == TEAM2_UGV:
                    cur_ent = GroundVehicle(loc=(col, row),map_only=self.team_home)
                    self.team2.append(cur_ent)
                    self.team_home[row][col] = TEAM2_BACKGROUND
                elif self._env[row][col] == TEAM2_UAV:
                    cur_ent = AerialVehicle(loc=(col, row),map_only=self.team_home)
                    self.team2.append(cur_ent)
                    self.team_home[row][col] = TEAM2_BACKGROUND

        self.create_observation_space()
        self.state = self.observation_space

        self.game_lost = False
        self.game_won = False

        return self.state

    def _render(self, mode="env", close=False):
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
