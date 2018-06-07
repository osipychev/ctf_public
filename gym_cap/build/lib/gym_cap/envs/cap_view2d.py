import sys

import pygame
from numpy.core.multiarray import ndarray
import numpy as np

from .const import *

QUIT = 12


class CaptureView2D:
    def __init__(self, game_name="Capture the Flag", screen_size=(400, 400)):

        # PyGame configurations
        pygame.init()
        pygame.display.set_caption(game_name)
        self.clock = pygame.time.Clock()

        # to show the right and bottom border
        self.screen = None
        self.__screen_size = screen_size

    def update_env(self, env):
        if self.screen is None:
            if len(env) != len(env[0]):
                self.__screen_size = (int(self.__screen_size[1] * (len(env) / len(env[0]))), self.__screen_size[1])
            self.screen = pygame.display.set_mode(self.__screen_size)
        tile_w = self.SCREEN_W / len(env)
        tile_h = self.SCREEN_H / len(env[0])
        map_h = len(env[0])
        map_w = len(env)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit(0)

        for x in range(map_w):
            for y in range(map_h):
                cur_color = COLOR_DICT[env[x][y]]
                if env[x][y] == TEAM1_UAV or env[x][y] == TEAM2_UAV:
                    pygame.draw.ellipse(self.screen, cur_color, [x * tile_w, y * tile_h, tile_w, tile_h])
                else:
                    pygame.draw.rect(self.screen, cur_color, (x * tile_w, y * tile_h, tile_w, tile_h))
        pygame.display.update()

    def human_move(self, env, team_home, team_list, move_suggestions):
        """
        Manual move controls

        Parameters
        ----------
        self        : object
            CapView object
        env         : list
            environment (fully observable)
        team_list   : list
            list of agents to move (can be blue or red team)
        """
        move_list = []
        tile_w = self.SCREEN_W / len(env)
        tile_h = self.SCREEN_H / len(env[0])
        i = 0
        # Cycle through agents
        while i < len(team_list):
            if not team_list[i].isAlive:
                i += 1
                continue
            # Only suggest moves once
            selected = team_list[i].get_loc()
            if team_list[i].air:
                pygame.draw.ellipse(self.screen, COLOR_DICT[SELECTED],
                                    [selected[0] * tile_w, selected[1] * tile_h, tile_w, tile_h])
            else:
                pygame.draw.rect(self.screen, COLOR_DICT[SELECTED],
                                 [selected[0] * tile_w, selected[1] * tile_h, tile_w, tile_h])
            # Draw circle on suggestions
            if RL_SUGGESTIONS:
                running_removed = 0
                removed_predict = 0
                for k in range(len(move_suggestions[i])):
                    if move_suggestions[i][k] < .15:
                        running_removed += move_suggestions[i][k]
                        move_suggestions[i][k] = 0
                        removed_predict += 1
                # Add removed probabilities to other options
                added_prob = running_removed / removed_predict
                for j in range(len(move_suggestions[i])):
                    if j == 0:
                        if move_suggestions[i][j] == 0:
                            continue
                        radius = int(tile_w / 2.0 * (move_suggestions[i][j]) ** .5)
                        pygame.draw.circle(self.screen, COLOR_DICT[SUGGESTION],
                                           (int(selected[0] * tile_w + tile_w / 2),
                                            int(selected[1] * tile_h + tile_h / 2)),
                                           radius)
                    elif j == 1 and selected[1] > 0:
                        if move_suggestions[i][j] == 0:
                            continue
                        radius = int(tile_w / 2.0 * (move_suggestions[i][j]) ** .5)
                        pygame.draw.circle(self.screen, COLOR_DICT[SUGGESTION],
                                           (int(selected[0] * tile_w + tile_w / 2),
                                            int((selected[1] - 1) * tile_h + tile_h / 2)),
                                           radius)
                    elif j == 2 and selected[0] < len(env) - 1:
                        if move_suggestions[i][j] == 0:
                            continue
                        radius = int(tile_w / 2.0 * (move_suggestions[i][j]) ** .5)
                        pygame.draw.circle(self.screen, COLOR_DICT[SUGGESTION],
                                           (int((selected[0] + 1) * tile_w + tile_w / 2),
                                            int(selected[1] * tile_h + tile_h / 2)),
                                           radius)
                    elif j == 3 and selected[1] < len(env[0]) - 1:
                        if move_suggestions[i][j] == 0:
                            continue
                        radius = int(tile_w / 2.0 * (move_suggestions[i][j]) ** .5)
                        pygame.draw.circle(self.screen, COLOR_DICT[SUGGESTION],
                                           (int(selected[0] * tile_w + tile_w / 2),
                                            int((selected[1] + 1) * tile_h + tile_h / 2)),
                                           radius)
                    elif j == 4 and selected[0] > 0:
                        if move_suggestions[i][j] == 0:
                            continue
                        radius = int(tile_w / 2.0 * (move_suggestions[i][j]) ** .5)
                        pygame.draw.circle(self.screen, COLOR_DICT[SUGGESTION],
                                           (int((selected[0] - 1) * tile_w + tile_w / 2),
                                            int(selected[1] * tile_h + tile_h / 2)),
                                           radius)

            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit(0)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Mouse button release event
                if event.type == pygame.MOUSEBUTTONUP:
                    x = int(mouse_x / tile_w)
                    y = int(mouse_y / tile_h)
                    # Moving unit north
                    if y < selected[1] and x == selected[0]:
                        team_list[i].move_selected = True
                        move_list.append(1)
                    # Moving unit east
                    elif y == selected[1] and x > selected[0]:
                        team_list[i].move_selected = True
                        move_list.append(2)
                    # Moving unit south
                    elif y > selected[1] and x == selected[0]:
                        team_list[i].move_selected = True
                        move_list.append(3)
                    # Moving unit west
                    elif y == selected[1] and x < selected[0]:
                        team_list[i].move_selected = True
                        move_list.append(4)
                    # No move
                    elif y == selected[1] and x == selected[0]:
                        team_list[i].move_selected = True
                        move_list.append(0)

                    if team_list[i].move_selected:
                        team_list[i].move_selected = False
                        if team_list[i].air:
                            pygame.draw.ellipse(self.screen, COLOR_DICT[COMPLETED],
                                                [selected[0] * tile_w, selected[1] * tile_h, tile_w, tile_h])
                        else:
                            pygame.draw.rect(self.screen, COLOR_DICT[COMPLETED],
                                             [selected[0] * tile_w, selected[1] * tile_h, tile_w, tile_h])
                        self.update_env(env)
                        i += 1
        return move_list

    def prep_prediction(self, env, team_home, team_list, i):
        """
        Replace all team members with normal background.
        ONLY FOR USE ON MODEL TRAINED WITH ONE AGENT.

        :param env: environment to modify
        :param team_home: background list
        :param team_list: list of team agents
        :param i: current agent to predict move for

        :return: modified environment
        """
        lx, ly = team_list[i].get_loc()
        model_env = np.copy(env)
        for x in range(len(model_env)):
            for y in range(len(model_env[x])):
                if x == lx and y == ly:
                    continue
                if model_env[x][y] == TEAM1_UGV or model_env[x][y] == TEAM1_UAV:
                    if team_home[x][y] == TEAM1_BACKGROUND:
                        model_env[x][y] = TEAM1_BACKGROUND
                    else:
                        model_env[x][y] = TEAM2_BACKGROUND
        return model_env

    @property
    def SCREEN_SIZE(self):
        return tuple(self.__screen_size)

    @property
    def SCREEN_W(self):
        return int(self.SCREEN_SIZE[0])

    @property
    def SCREEN_H(self):
        return int(self.SCREEN_SIZE[1])
