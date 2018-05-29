import random
import sys

import gym
from gym import spaces
from gym.utils import seeding
from pandas import *

from .agent import *
from .enemy_ai import EnemyAI
from .cap_view2d import CaptureView2D
from .create_map import CreateMap

"""
Requires that all units initially exist in home zone.
"""


class CapEnv(gym.Env):
    metadata = {
        "render.modes": ["fast", "human"],
    }

    ACTION = ["X", "N", "E", "S", "W"]

    def __init__(self, map_size=20, mode="random", in_seed=None):
        """
        Constructor

        Parameters
        ----------
        self    : object
            CapEnv object
        """
        self._reset(map_size, mode=mode)

    def _reset(self, map_size=None, in_seed=None, mode=None):
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
        # If seed not defined, define it
        # If in_seed is not None, set seed to its value
        self.in_seed = in_seed

        if map_size is None:
            self._env = CreateMap.gen_map('map', dim=self.map_size[0], in_seed=self.in_seed)
        else:
            self._env = CreateMap.gen_map('map', map_size, in_seed=self.in_seed)

        self.map_size = (len(self._env), len(self._env[0]))
        self.team_home = self._env.copy()

        self.team1 = []
        self.team2 = []
        for y in range(len(self._env)):
            for x in range(len(self._env[0])):
                if self._env[x][y] == TEAM1_UGV:
                    cur_ent = GroundVehicle([x, y], self.team_home, 1)
                    self.team1.insert(0, cur_ent)
                    self.team_home[x][y] = TEAM1_BACKGROUND
                elif self._env[x][y] == TEAM1_UAV:
                    cur_ent = AerialVehicle([x, y], self.team_home, 1)
                    self.team1.append(cur_ent)
                    self.team_home[x][y] = TEAM1_BACKGROUND
                elif self._env[x][y] == TEAM2_UGV:
                    cur_ent = GroundVehicle([x, y], self.team_home, 2)
                    self.team2.insert(0, cur_ent)
                    self.team_home[x][y] = TEAM2_BACKGROUND
                elif self._env[x][y] == TEAM2_UAV:
                    cur_ent = AerialVehicle([x, y], self.team_home, 2)
                    self.team2.append(cur_ent)
                    self.team_home[x][y] = TEAM2_BACKGROUND

        # print(DataFrame(self._env))
        # place arial units at end of list
        for i in range(len(self.team1)):
            if self.team1[i].air:
                self.team1.insert(len(self.team1), self.team1.pop(i))
        for i in range(len(self.team2)):
            if self.team2[i].air:
                self.team2.insert(len(self.team2) - 1, self.team2.pop(i))

        self.action_space = spaces.Discrete(len(self.ACTION) ** (NUM_BLUE + NUM_UAV))

        self.game_lost = False
        self.game_won = False

        self.create_observation_space(RED)
        self.create_observation_space(BLUE)
        self.state = self.observation_space
        self.cap_view = CaptureView2D(screen_size=(500, 500))
        self.viewer = None
        if not mode is None:
            self.mode = mode

        self.game_lost = False
        self.game_won = False
        self.cur_step = 0

        # Necessary for human mode
        self.first = True

        self._seed()

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
        for i in range(len(self.team2)):
            if not self.team2[i].isAlive:
                reward += (50.0 / len(self.team2))
        for i in range(len(self.team1)):
            if not self.team1[i].isAlive:
                reward -= (50.0 / len(self.team1))

        # 10,000 steps returns -.5
        # map_size_2 = map_size[0]*map_size[1]
        # reward-=(.5/map_size_2)
        reward -= (50.0 / 1000) * self.cur_step
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

    def individual_reward(self):
        # Small reward range [-1, 1]
        all_small_obs = []
        all_small_reward = []
        for agent in self.team1:
            lx, ly = agent.get_loc()
            small_observation = [[-1 for i in range(2 * agent.range + 1)] for j in range(2 * agent.range + 1)]
            small_reward = 0
            for x in range(lx - agent.range, lx + agent.range + 1):
                for y in range(ly - agent.range, ly + agent.range + 1):
                    if ((x-lx) ** 2 + (y-ly) ** 2 <= agent.range ** 2) and \
                            0 <= x < self.map_size[0] and \
                            0 <= y < self.map_size[1]:
                        small_observation[x - lx + agent.range][y - ly + agent.range] = self._env[x][y]
                        # Max reward for finding red flag
                        if self._env[x][y] == TEAM2_FLAG:
                            small_reward = .5
                        # Reward for UAV finding enemy wherever
                        elif agent.air and self._env[x][y] == TEAM2_UGV:
                            small_reward += .5/NUM_RED
                        # Reward for finding a vulnerable enemy
                        elif self._env[x][y] == TEAM2_UGV and \
                                self.team_home[x][y] == TEAM1_BACKGROUND and \
                                self.team_home[lx][ly] == TEAM1_BACKGROUND:
                            small_reward += .5/NUM_RED
                        # Neg Reward for finding an enemy when you're vulnerable
                        elif self._env[x][y] == TEAM2_UGV and \
                                self.team_home[x][y] == TEAM2_BACKGROUND and \
                                self.team_home[lx][ly] == TEAM2_BACKGROUND:
                            small_reward -= .5/NUM_BLUE
            all_small_obs.append(small_observation)
            all_small_reward.append(small_reward)
        return all_small_obs, all_small_reward

    def create_observation_space(self, team=BLUE):
        """
        Creates the observation space in self.observation_space

        Parameters
        ----------
        self    : object
            CapEnv object
        team    : int
            Team to create obs space for
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
                        if (i * i + j * j <= agent.range ** 2) and \
                                not (locx < 0 or locx > self.map_size[0] - 1) and \
                                not (locy < 0 or locy > self.map_size[1] - 1):
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
                        if (i * i + j * j <= agent.range ** 2) and \
                                not (locx < 0 or locx > self.map_size[0] - 1) and \
                                not (locy < 0 or locy > self.map_size[1] - 1):
                            self.observation_space2[locx][locy] = self._env[locx][locy]

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
            loc = self.team1[entity_num].get_loc()
            cur_range = self.team1[entity_num].a_range
            for x in range(-cur_range, cur_range + 1):
                for y in range(-cur_range, cur_range + 1):
                    locx, locy = x + loc[0], y + loc[1]
                    if (x * x + y * y <= cur_range ** 2) and \
                            not (locx < 0 or locx > self.map_size[0] - 1) and \
                            not (locy < 0 or locy > self.map_size[1] - 1):
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
            for x in range(-cur_range, cur_range + 1):
                for y in range(-cur_range, cur_range + 1):
                    locx, locy = x + loc[0], y + loc[1]
                    if (x * x + y * y <= cur_range ** 2) and \
                            not (locx < 0 or locx > self.map_size[0] - 1) and \
                            not (locy < 0 or locy > self.map_size[1] - 1):
                        if self._env[locx][locy] == TEAM1_UGV:
                            if self.team_home[locx][locy] == TEAM2_BACKGROUND:
                                for i in range(len(self.team1)):
                                    enemy_locx, enemy_locy = self.team1[i].get_loc()
                                    if enemy_locx == locx and enemy_locy == locy:
                                        self.team1[i].isAlive = False
                                        self._env[locx][locy] = DEAD
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
        # print(DataFrame(self._env))
        self.cur_step += 1
        move_list = []

        # ERROR checking
        if type(entities_action) is int:
            if entities_action >= len(self.ACTION) ** (NUM_BLUE + NUM_UAV):
                sys.exit("ERROR: You entered too many moves. \
                         There are " + str(NUM_BLUE + NUM_UAV) + " entities.")
            while len(move_list) < (NUM_BLUE + NUM_UAV):
                move_list.append(entities_action % 5)
                entities_action = int(entities_action / 5)
        else:
            if len(entities_action) > NUM_BLUE + NUM_UAV:
                sys.exit("ERROR: You entered too many moves. \
                         There are " + str(NUM_BLUE + NUM_UAV) + " entities.")
            move_list = entities_action

        # TODO
        # Get team2 actions from heuristic function
        # team2_actions = generate_actions()

        # Move team2
        team2_actions = 0
        if self.mode == "run_away":
            team2_actions = generate_run_actions()
        elif self.mode == "defend":
            team2_actions = EnemyAI.patrol(self.team2)
        elif self.mode == "attack":
            team2_actions = self.action_space.sample()
        elif self.mode == "sandbox":
            for i in range(len(self.team2)):
                locx, locy = self.team2[i].get_loc()
                if self.team2[i].atHome:
                    self._env[locx][locy] = TEAM2_BACKGROUND
                else:
                    self._env[locx][locy] = TEAM1_BACKGROUND
            self.team2 = []
        elif self.mode == "patrol":
            for agent in self.team2:
                team2_actions.append(agent.ai.patrol(agent, self.observation_space2, self.team2))
        elif self.mode == "random":
            team2_actions = random.randint(0, len(self.ACTION) ** (NUM_RED + NUM_UAV))  # choose random action
        elif self.mode == "human":
            self._render("env")
            team2_actions = self.cap_view.human_move(self._env, self.team2)

        # Move team1
        for i in range(len(self.team1)):
            self.team1[i].move(self.ACTION[move_list[i]], self._env, self.team_home)

        # Allows for both an integer and a list input
        move_list = []
        if isinstance(team2_actions, int):
            for i in range(len(self.team2)):
                move_list.append(team2_actions % 5)
                team2_actions = team2_actions // 5
        else:
            move_list = team2_actions

        i = 0
        for agent in self.team2:
            if agent.isAlive:
                agent.move_selected = False
                agent.move(self.ACTION[move_list[i]], self._env, self.team_home)
                i += 1

        # Check for dead
        for i in range(len(self.team1)):
            if not self.team1[i].atHome or self.team1[i].air or not self.team1[i].isAlive:
                continue
            self.check_dead(i, 1)
        for i in range(len(self.team2)):
            if not self.team2[i].atHome or self.team2[i].air or not self.team2[i].isAlive:
                continue
            self.check_dead(i, 2)

        # Check win and lose conditions
        has_alive_entity = False
        for i in self.team2:
            if i.isAlive and not i.air:
                has_alive_entity = True
                locx, locy = i.get_loc()
                if self.team_home[locx][locy] == TEAM1_FLAG:
                    self.game_lost = True

        if not has_alive_entity and self.mode != "sandbox":
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
        self.individual_reward()
        # self.create_observation_space(RED)
        # self.state = self.observation_space
        self.state = self._env

        isDone = False
        if self.game_won or self.game_lost:
            isDone = True
        info = {}

        return self.state, reward, isDone, info

    def render(self, mode="human"):
        """
        Renders the screen options="obs, env"

        Parameters
        ----------
        self    : object
            CapEnv object
        mode    : string
            Defines what will be rendered
        """
        SCREEN_W = 800
        SCREEN_H = 800
        env = self._env

        from gym.envs.classic_control import rendering
        if self.viewer is None:
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

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')
        # print(self._env)

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
        if mode == "env":
            self.cap_view.update_env(self._env)
        elif mode == "obs":
            self.cap_view.update_env(self.observation_space)
        elif mode == "obs2":
            self.cap_view.update_env(self.observation_space2)
        elif mode == "team":
            self.cap_view.update_env(self.team_home)
        return

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None


# Different environment sizes and modes
# Random modes
class CapEnvGenerate20x20Random(CapEnv):
    def __init__(self, mode="random"):
        super(CapEnvGenerate20x20Random, self).__init__(map_size=20, mode=mode)


class CapEnvGenerate100x100Random(CapEnv):
    def __init__(self, mode="random"):
        super(CapEnvGenerate100x100Random, self).__init__(map_size=100, mode=mode)


class CapEnvGenerate500x500Random(CapEnv):
    def __init__(self, mode="random"):
        super(CapEnvGenerate500x500Random, self).__init__(map_size=500, mode=mode)


# Human modes
class CapEnvGenerate20x20Human(CapEnv):
    def __init__(self, mode="human"):
        super(CapEnvGenerate20x20Human, self).__init__(map_size=20, mode=mode)


class CapEnvGenerate100x100Human(CapEnv):
    def __init__(self, mode="human"):
        super(CapEnvGenerate100x100Human, self).__init__(map_size=100, mode=mode)


class CapEnvGenerate500x500Human(CapEnv):
    def __init__(self, mode="human"):
        super(CapEnvGenerate500x500Human, self).__init__(map_size=500, mode=mode)


# Sandbox modes
class CapEnvGenerate20x20Sandbox(CapEnv):
    def __init__(self, mode="sandbox"):
        super(CapEnvGenerate20x20Sandbox, self).__init__(map_size=20, mode=mode)


class CapEnvGenerate100x100Sandbox(CapEnv):
    def __init__(self, mode="sandbox"):
        super(CapEnvGenerate100x100Sandbox, self).__init__(map_size=100, mode=mode)


class CapEnvGenerate500x500Sandbox(CapEnv):
    def __init__(self, mode="sandbox"):
        super(CapEnvGenerate500x500Sandbox, self).__init__(map_size=500, mode=mode)
# DEBUGGING
# if __name__ == "__main__":
# cap_env = CapEnv(env_matrix_file="ctf_samples/cap2d_000.npy")
