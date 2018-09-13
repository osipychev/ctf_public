import random
import sys

import gym
from gym import spaces
from gym.utils import seeding
import numpy as np

from .agent import *
from .cap_view2d import CaptureView2D
from .create_map import CreateMap

"""
Requires that all units initially exist in home zone.
"""


class CapEnv(gym.Env):
    metadata = {
        "render.modes": ["fast", "human", 'rgb_array'],
        'video.frames_per_second' : 50
    }

    ACTION = ["X", "N", "E", "S", "W"]

    def __init__(self, map_size=20, mode="random"):
        """
        Constructor

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        self.seed()
        self.reset(map_size, mode=mode)
        self.viewer = None

    def reset(self, map_size=None, mode="random", render_mode="env", policy_blue=None, policy_red=None):
        """
        Resets the game

        :param map_size: Size of the map
        :param mode: Action generation mode
        :param render_mode: what to render
        :return: void

        """
        self.render_mode = render_mode

        if map_size is None:
            self._env = CreateMap.gen_map('map', dim=self.map_size[0])
        else:
            self._env = CreateMap.gen_map('map', map_size)

        self.map_size = (len(self._env), len(self._env[0]))
        self.team_home = self._env.copy()

        self.team_blue = []
        self.team_red = []

        if policy_blue is not None: self.policy_blue = policy_blue
        if policy_red is not None: self.policy_red = policy_red

        for y in range(len(self._env)):
            for x in range(len(self._env[0])):
                if self._env[x][y] == TEAM1_UGV:
                    cur_ent = GroundVehicle([x, y], self.team_home, 1)
                    self.team_blue.insert(0, cur_ent)
                    self.team_home[x][y] = TEAM1_BACKGROUND
                elif self._env[x][y] == TEAM1_UAV:
                    cur_ent = AerialVehicle([x, y], self.team_home, 1)
                    self.team_blue.append(cur_ent)
                    self.team_home[x][y] = TEAM1_BACKGROUND
                elif self._env[x][y] == TEAM2_UGV:
                    cur_ent = GroundVehicle([x, y], self.team_home, 2)
                    self.team_red.insert(0, cur_ent)
                    self.team_home[x][y] = TEAM2_BACKGROUND
                elif self._env[x][y] == TEAM2_UAV:
                    cur_ent = AerialVehicle([x, y], self.team_home, 2)
                    self.team_red.append(cur_ent)
                    self.team_home[x][y] = TEAM2_BACKGROUND

        # print(DataFrame(self._env))
        # place arial units at end of list
        for i in range(len(self.team_blue)):
            if self.team_blue[i].air:
                self.team_blue.insert(len(self.team_blue), self.team_blue.pop(i))
        for i in range(len(self.team_red)):
            if self.team_red[i].air:
                self.team_red.insert(len(self.team_red) - 1, self.team_red.pop(i))

        self.action_space = spaces.Discrete(len(self.ACTION) ** (NUM_BLUE + NUM_UAV))

        self.game_lost = False
        self.game_won = False

        self.create_observation_space()
        self.state = self.observation_space_blue
        self.cap_view = CaptureView2D(screen_size=(500, 500))
        self.mode = mode

        self.game_lost = False
        self.game_won = False
        self.cur_step = 0

        # Necessary for human mode
        self.first = True


        return self.state

    def create_reward(self):
        """
        Range (-100, 100)

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        reward = 0
        # Win and loss return max rewards
        # if self.game_lost:
        # return -1
        # if self.game_won:
        # return 1

        # Dead enemy team gives .5/total units for each dead unit
        for i in range(len(self.team_red)):
            if not self.team_red[i].isAlive:
                reward += (50.0 / len(self.team_red))
        for i in range(len(self.team_blue)):
            if not self.team_blue[i].isAlive:
                reward -= (50.0 / len(self.team_blue))

        # 10,000 steps returns -.5
        # map_size_2 = map_size[0]*map_size[1]
        # reward-=(.5/map_size_2)
        #reward -= (50.0 / 1000) * self.cur_step
        if self.game_won:
            reward += 100
        if reward <= -100:
            reward = -100
            self.game_lost = True

        # if self.cur_step > 10000:
        # reward-=.5
        # else:
        # reward-=((self.cur_step/10000.0)*.5)
        return reward

    def create_observation_space(self):
        """
        Creates the observation space in self.observation_space

        Parameters
        ----------
        self    : object
            CapEnv object
        team    : int
            Team to create obs space for
        """

        self.observation_space_blue = np.full((self.map_size[0], self.map_size[1]), -1)
        for agent in self.team_blue:
            if not agent.isAlive:
                continue
            loc = agent.get_loc()
            for i in range(-agent.range, agent.range + 1):
                for j in range(-agent.range, agent.range + 1):
                    locx, locy = i + loc[0], j + loc[1]
                    if (i * i + j * j <= agent.range ** 2) and \
                            not (locx < 0 or locx > self.map_size[0] - 1) and \
                            not (locy < 0 or locy > self.map_size[1] - 1):
                        self.observation_space_blue[locx][locy] = self._env[locx][locy]

        self.observation_space_red = np.full((self.map_size[0], self.map_size[1]), -1)
        for agent in self.team_red:
            if not agent.isAlive:
                continue
            loc = agent.get_loc()
            for i in range(-agent.range, agent.range + 1):
                for j in range(-agent.range, agent.range + 1):
                    locx, locy = i + loc[0], j + loc[1]
                    if (i * i + j * j <= agent.range ** 2) and \
                            not (locx < 0 or locx > self.map_size[0] - 1) and \
                            not (locy < 0 or locy > self.map_size[1] - 1):
                        self.observation_space_red[locx][locy] = self._env[locx][locy]
    @property
    def get_team_blue(self):
        return np.copy(self.team_blue)

    @property
    def get_team_red(self):
        return np.copy(self.team_red)

    @property
    def get_map(self):
        return np.copy(self.team_home)

    @property
    def get_obs_blue(self):
        return np.copy(self.observation_space_blue)

    @property
    def get_obs_red(self):
        return np.copy(self.observation_space_red)



    # TODO improve
    # Change from range to attack range
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
            loc = self.team_blue[entity_num].get_loc()
            cur_range = self.team_blue[entity_num].a_range
            for x in range(-cur_range, cur_range + 1):
                for y in range(-cur_range, cur_range + 1):
                    locx, locy = x + loc[0], y + loc[1]
                    if (x * x + y * y <= cur_range ** 2) and \
                            not (locx < 0 or locx > self.map_size[0] - 1) and \
                            not (locy < 0 or locy > self.map_size[1] - 1):
                        if self._env[locx][locy] == TEAM2_UGV:
                            if self.team_home[locx][locy] == TEAM1_BACKGROUND:
                                for i in range(len(self.team_red)):
                                    enemy_locx, enemy_locy = self.team_red[i].get_loc()
                                    if enemy_locx == locx and enemy_locy == locy:
                                        self.team_red[i].isAlive = False
                                        self._env[locx][locy] = DEAD
                                        break
        elif team == 2:
            loc = self.team_red[entity_num].get_loc()
            cur_range = self.team_red[entity_num].a_range
            for x in range(-cur_range, cur_range + 1):
                for y in range(-cur_range, cur_range + 1):
                    locx, locy = x + loc[0], y + loc[1]
                    if (x * x + y * y <= cur_range ** 2) and \
                            not (locx < 0 or locx > self.map_size[0] - 1) and \
                            not (locy < 0 or locy > self.map_size[1] - 1):
                        if self._env[locx][locy] == TEAM1_UGV:
                            if self.team_home[locx][locy] == TEAM2_BACKGROUND:
                                for i in range(len(self.team_blue)):
                                    enemy_locx, enemy_locy = self.team_blue[i].get_loc()
                                    if enemy_locx == locx and enemy_locy == locy:
                                        self.team_blue[i].isAlive = False
                                        self._env[locx][locy] = DEAD
                                        break

    def seed(self, seed=None):
        """
        todo docs still

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, entities_action=None, cur_suggestions=None):
        """
        Takes one step in the cap the flag game



        :param
            entities_action: contains actions for entity 1-n
            cur_suggestions: suggestions from rl to human
        :return:
            state    : object
            CapEnv object
            reward  : float
            float containing the reward for the given action
            isDone  : bool
            decides if the game is over
            info    :
        """

        self.cur_step += 1
        move_list = []

        # Get actions from uploaded policies
        try:
            move_list_red = self.policy_red.gen_action(self.team_red,self.observation_space_red,free_map=self.team_home)
        except:
            print("No valid policy for red team")
            exit()

        if entities_action == None:
            try:
                move_list_blue = self.policy_blue.gen_action(self.team_blue,self.observation_space_blue,free_map=self.team_home)
            except:
                print("No valid policy for blue team and no actions provided")
                exit()
        elif type(entities_action) is int:
            if entities_action >= len(self.ACTION) ** (NUM_BLUE + NUM_UAV):
                sys.exit("ERROR: You entered too many moves. \
                         There are " + str(NUM_BLUE + NUM_UAV) + " entities.")
            while len(move_list) < (NUM_BLUE + NUM_UAV):
                move_list_blue.append(entities_action % 5)
                entities_action = int(entities_action / 5)
        else:
            if len(entities_action) > NUM_BLUE + NUM_UAV:
                sys.exit("ERROR: You entered too many moves. \
                         There are " + str(NUM_BLUE + NUM_UAV) + " entities.")
            move_list_blue = entities_action


        # Move team1
        for idx, act in enumerate(move_list_blue):
            self.team_blue[idx].move(self.ACTION[act], self._env, self.team_home)

        # Move team2
        for idx, act in enumerate(move_list_red):
            self.team_red[idx].move(self.ACTION[act], self._env, self.team_home)


        # Check for dead
        for i in range(len(self.team_blue)):
            if not self.team_blue[i].atHome or self.team_blue[i].air or not self.team_blue[i].isAlive:
                continue
            self.check_dead(i, 1)
        for i in range(len(self.team_red)):
            if not self.team_red[i].atHome or self.team_red[i].air or not self.team_red[i].isAlive:
                continue
            self.check_dead(i, 2)

        # Check win and lose conditions
        has_alive_entity = False
        for i in self.team_red:
            if i.isAlive and not i.air:
                has_alive_entity = True
                locx, locy = i.get_loc()
                if self.team_home[locx][locy] == TEAM1_FLAG:
                    self.game_lost = True

        # TODO Change last condition for multi agent model
        if not has_alive_entity and self.mode != "sandbox" and self.mode != "human_blue":
            self.game_won = True
            self.game_lost = False
        has_alive_entity = False
        for i in self.team_blue:
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

        self.create_observation_space()
        # self.individual_reward()
        # self.state = self.observation_space
        self.state = self._env

        isDone = False
        if self.game_won or self.game_lost:
            isDone = True
        info = {}

        return self.state, reward, isDone, info

    def render(self, mode='human'):
        """
        Renders the screen options="obs, env"

        Parameters
        ----------
        self    : object
            CapEnv object
        mode    : string
            Defines what will be rendered
        """
        SCREEN_W = 600
        SCREEN_H = 600

        if self.render_mode == "env":
            env = self._env
        elif self.render_mode == "blue":
            env = self.observation_space_blue
        elif self.render_mode == "red":
            env = self.observation_space_red

        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(SCREEN_W, SCREEN_H)
            self.viewer.set_bounds(0, SCREEN_W, 0, SCREEN_H)

        tile_w = SCREEN_W / len(env)
        tile_h = SCREEN_H / len(env[0])
        map_h = len(env[0])
        map_w = len(env)

        self.viewer.draw_polygon([(0, 0), (SCREEN_W, 0), (SCREEN_W, SCREEN_H), (0, SCREEN_H)], color=(0, 0, 0))

        for row in range(map_h):
            for col in range(map_w):
                cur_color = np.divide(COLOR_DICT[env[row][col]], 255)
                if env[row][col] == TEAM1_UAV or env[row][col] == TEAM2_UAV:
                    self.viewer.draw_circle(tile_w / 2, 20, color=cur_color).add_attr([col * tile_w, row * tile_h])
                else:
                    self.viewer.draw_polygon([
                        (col * tile_w, row * tile_h),
                        (col * tile_w + tile_w, row * tile_h),
                        (col * tile_w + tile_w, row * tile_h + tile_h),
                        (col * tile_w, row * tile_h + tile_h)], color=cur_color)

        return self.viewer.render(return_rgb_array = mode=='rgb_array')

    def close(self):
        if self.viewer: self.viewer.close()


    # def quit_game(self):
    #     if self.viewer is not None:
    #         self.viewer.close()
    #         self.viewer = None


# Different environment sizes and modes
# Random modes
class CapEnvGenerate(CapEnv):
    def __init__(self):
        super(CapEnvGenerate, self).__init__(map_size=20)


# DEBUGGING
# if __name__ == "__main__":
# cap_env = CapEnv(env_matrix_file="ctf_samples/cap2d_000.npy")
