import random
import sys

import gym
from gym import spaces
from gym.utils import seeding
import numpy as np

from .agent import *
from .const import *
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
        self.num_blue_ugv = NUM_BLUE
        self.num_blue_uav = NUM_UAV
        self.num_red_ugv = NUM_RED
        self.num_red_uav = NUM_UAV
        self.num_grey = NUM_GRAY

        self.seed()
        self.reset(map_size, mode=mode)
        self.viewer = None
        if STOCH_ATTACK:
            self.interaction = self._interaction_stoch
        else: self.interaction = self._interaction_determ

    def reset(self, map_size=None, mode="random", policy_blue=None, policy_red=None):
        """
        Resets the game

        :param map_size: Size of the map
        :param mode: Action generation mode
        :return: void

        """

        map_obj = [self.num_blue_ugv, self.num_blue_uav, self.num_red_ugv, self.num_red_uav, self.num_grey]
        if map_size is None:
            self._env, self.team_home = CreateMap.gen_map('map', dim=self.map_size[0], rand_zones=STOCH_ZONES, np_random=self.np_random, map_obj=map_obj)
        else:
            self._env, self.team_home = CreateMap.gen_map('map', map_size, rand_zones=STOCH_ZONES, np_random=self.np_random, map_obj=map_obj)

        self.map_size = (len(self._env), len(self._env[0]))

        if policy_blue is not None: self.policy_blue = policy_blue
        if policy_red is not None: self.policy_red = policy_red

        self.action_space = spaces.Discrete(len(self.ACTION) ** (NUM_BLUE + NUM_UAV))

        self.blue_win = False
        self.red_win = False

        self.team_blue, self.team_red = self._map_to_list(self._env, self.team_home)

        self.create_observation_space()

        self.mode = mode

        if NUM_RED == 0:
            self.mode = "sandbox"

        self.blue_win = False
        self.red_win = False

        # Necessary for human mode
        self.first = True

        return self.observation_space_blue

    def _map_to_list(self, complete_map, static_map):
        """
        From given map, it generates objects of agents and push them to list

        self            : objects
        complete_map    : 2d numpy array
        static_map      : 2d numpy array
        """
        team_blue = []
        team_red = []

        for y in range(len(complete_map)):
            for x in range(len(complete_map[0])):
                if complete_map[x][y] == TEAM1_UGV:
                    cur_ent = GroundVehicle([x, y], static_map, TEAM1_BACKGROUND)
                    team_blue.append(cur_ent)
                elif complete_map[x][y] == TEAM1_UAV:
                    cur_ent = AerialVehicle([x, y], static_map, TEAM1_BACKGROUND)
                    team_blue.insert(0, cur_ent)
                elif complete_map[x][y] == TEAM2_UGV:
                    cur_ent = GroundVehicle([x, y], static_map, TEAM2_BACKGROUND)
                    team_red.append(cur_ent)
                elif complete_map[x][y] == TEAM2_UAV:
                    cur_ent = AerialVehicle([x, y], static_map, TEAM2_BACKGROUND)
                    team_red.insert(0, cur_ent)

        return team_blue, team_red

    def create_reward(self):
        """
        Range (-100, 100)

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        reward = 0

        if self.blue_win:
            return 100
        if self.red_win:
            return -100

        # Dead enemy team gives .5/total units for each dead unit
        for i in range(len(self.team_red)):
            if not self.team_red[i].isAlive:
                reward += (50.0 / len(self.team_red))
        for i in range(len(self.team_blue)):
            if not self.team_blue[i].isAlive:
                reward -= (50.0 / len(self.team_blue))

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

        self.observation_space_blue = np.full_like(self._env, -1)
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

        self.observation_space_red = np.full_like(self._env, -1)
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

        # TODO need to be added observation for grey team
        self.observation_space_grey = np.full_like(self._env, -1)

    @property
    def get_full_state(self):
        return np.copy(self._env)

    @property
    def get_team_blue(self):
        return np.copy(self.team_blue)

    @property
    def get_team_red(self):
        return np.copy(self.team_red)

    @property
    def get_team_grey(self):
        return np.copy(self.team_grey)

    @property
    def get_map(self):
        return np.copy(self.team_home)

    @property
    def get_obs_blue(self):
        return np.copy(self.observation_space_blue)

    @property
    def get_obs_red(self):
        return np.copy(self.observation_space_red)

    @property
    def get_obs_grey(self):
        return np.copy(self.observation_space_grey)


    def _interaction_determ(self, entity):
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
        loc = entity.get_loc()
        cur_range = entity.a_range
        for x in range(-cur_range, cur_range + 1):
            for y in range(-cur_range, cur_range + 1):
                locx, locy = x + loc[0], y + loc[1]
                if (x * x + y * y <= cur_range ** 2) and \
                        not (locx < 0 or locx > self.map_size[0] - 1) and \
                        not (locy < 0 or locy > self.map_size[1] - 1):
                    if entity.team == TEAM1_BACKGROUND and self._env[locx][locy] == TEAM2_UGV:
                        if self.team_home[loc] == TEAM2_BACKGROUND:
                            entity.isAlive = False
                            self._env[loc] = DEAD
                            break
                    elif entity.team == TEAM2_BACKGROUND and self._env[locx][locy] == TEAM1_UGV:
                        if self.team_home[loc] == TEAM1_BACKGROUND:
                            entity.isAlive = False
                            self._env[loc] = DEAD
                            break

    def _interaction_stoch(self, entity):
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
        loc = entity.get_loc()
        cur_range = entity.a_range
        n_friends = 0
        n_enemies = 0
        flag = False
        if entity.team == self.team_home[loc]:
            n_friends += 1
        else:
            n_enemies += 1

        for x in range(-cur_range, cur_range + 1):
            for y in range(-cur_range, cur_range + 1):
                locx, locy = x + loc[0], y + loc[1]
                if (x * x + y * y <= cur_range ** 2) and \
                        not (locx < 0 or locx > self.map_size[0] - 1) and \
                        not (locy < 0 or locy > self.map_size[1] - 1):
                    if entity.team == TEAM1_BACKGROUND and self._env[locx][locy] == TEAM2_UGV:
                        n_enemies += 1
                        flag = True
                    elif entity.team == TEAM2_BACKGROUND and self._env[locx][locy] == TEAM1_UGV:
                        n_enemies += 1
                        flag = True
                    elif entity.team == TEAM1_BACKGROUND and self._env[locx][locy] == TEAM1_UGV:
                        n_friends += 1
                    elif entity.team == TEAM2_BACKGROUND and self._env[locx][locy] == TEAM2_UGV:
                        n_friends += 1
        if flag and self.np_random.rand() > n_friends/(n_friends + n_enemies):

            entity.isAlive = False
            self._env[loc] = DEAD

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
            if STOCH_TRANSITIONS and self.np_random.rand() < 0.1:
                act = self.np_random.randint(0,len(self.ACTION))
            self.team_blue[idx].move(self.ACTION[act], self._env, self.team_home)

        # Move team2
        for idx, act in enumerate(move_list_red):
            if STOCH_TRANSITIONS and self.np_random.rand() < 0.1:
                act = self.np_random.randint(0,len(self.ACTION))
            self.team_red[idx].move(self.ACTION[act], self._env, self.team_home)


        # Check for dead
        for entity in self.team_blue:
            if entity.air or not entity.isAlive:
                continue
            self.interaction(entity)
        for entity in self.team_red:
            if entity.air or not entity.isAlive:
                continue
            self.interaction(entity)

        # Check win and lose conditions
        has_alive_entity = False
        for i in self.team_red:
            if i.isAlive and not i.air:
                has_alive_entity = True
                locx, locy = i.get_loc()
                if self.team_home[locx][locy] == TEAM1_FLAG:
                    self.red_win = True
        # TODO Change last condition for multi agent model
        if not has_alive_entity and self.mode != "sandbox" and self.mode != "human_blue":
            self.blue_win = True

        has_alive_entity = False
        for i in self.team_blue:
            if i.isAlive and not i.air:
                has_alive_entity = True
                locx, locy = i.get_loc()
                if self.team_home[locx][locy] == TEAM2_FLAG:
                    self.blue_win = True
        if not has_alive_entity:
            self.red_win = True

        reward = self.create_reward()

        self.create_observation_space()

        self.state = np.copy(self._env)

        isDone = self.red_win or self.blue_win
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

        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(SCREEN_W, SCREEN_H)
            self.viewer.set_bounds(0, SCREEN_W, 0, SCREEN_H)

        self.viewer.draw_polygon([(0, 0), (SCREEN_W, 0), (SCREEN_W, SCREEN_H), (0, SCREEN_H)], color=(0, 0, 0))

        self._env_render(self.team_home,
                        [10, 10], [SCREEN_W//2-10, SCREEN_H//2-10])
        self._env_render(self.observation_space_blue,
                        [10+SCREEN_W//2, 10], [SCREEN_W//2-10, SCREEN_H//2-10])
        self._env_render(self.observation_space_red,
                        [10+SCREEN_W//2, 10+SCREEN_H//2], [SCREEN_W//2-10, SCREEN_H//2-10])
        self._env_render(self._env,
                        [10, 10+SCREEN_H//2], [SCREEN_W//2-10, SCREEN_H//2-10])

        return self.viewer.render(return_rgb_array = mode=='rgb_array')

    def _env_render(self, env, rend_loc, rend_size):
        map_h = len(env[0])
        map_w = len(env)

        tile_w = rend_size[0] / len(env)
        tile_h = rend_size[1] / len(env[0])

        for y in range(map_h):
            for x in range(map_w):
                locx, locy = rend_loc
                locx += x * tile_w
                locy += y * tile_h
                cur_color = np.divide(COLOR_DICT[env[x][y]], 255.0)
                self.viewer.draw_polygon([
                    (locx, locy),
                    (locx + tile_w, locy),
                    (locx + tile_w, locy + tile_h),
                    (locx, locy + tile_h)], color=cur_color)

                if env[x][y] == TEAM1_UAV or env[x][y] == TEAM2_UAV:
                    self.viewer.draw_polyline([
                        (locx, locy),
                        (locx + tile_w, locy + tile_h)],
                        color=(0,0,0), linewidth=2)
                    self.viewer.draw_polyline([
                        (locx + tile_w, locy),
                        (locx, locy + tile_h)],
                        color=(0,0,0), linewidth=2)#col * tile_w, row * tile_h

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
