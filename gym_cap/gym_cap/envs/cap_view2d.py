import pygame
import random
import numpy as np
import os
from .const import *
from pandas import *

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
        if self.screen == None:
            if (len(env) != len(env[0])):
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

        for x in range(map_w):
            for y in range(map_h):
                cur_color = COLOR_DICT[env[x][y]]
                if env[x][y] == TEAM1_UAV or env[x][y] == TEAM2_UAV:
                    pygame.draw.ellipse(self.screen, cur_color, [x * tile_w, y * tile_h, tile_w, tile_h])
                else:
                    pygame.draw.rect(self.screen, cur_color, (x * tile_w, y * tile_h, tile_w, tile_h))
        pygame.display.update()

    def human_move(self, env, team_list):
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
            selected = team_list[i].get_loc()
            if team_list[i].air:
                pygame.draw.ellipse(self.screen, COLOR_DICT[SELECTED],
                                    [selected[0] * tile_w, selected[1] * tile_h, tile_w, tile_h])
            else:
                pygame.draw.rect(self.screen, COLOR_DICT[SELECTED],
                                 [selected[0] * tile_w, selected[1] * tile_h, tile_w, tile_h])
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
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
                        if team_list[i].air:
                            pygame.draw.ellipse(self.screen, COLOR_DICT[COMPLETED],
                                                [selected[0] * tile_w, selected[1] * tile_h, tile_w, tile_h])
                        else:
                            pygame.draw.rect(self.screen, COLOR_DICT[COMPLETED],
                                             [selected[0] * tile_w, selected[1] * tile_h, tile_w, tile_h])
                        i += 1
        return move_list

    def quit_game(self):
        try:
            pygame.display.quit()
            pygame.quit()
        except Exception:
            pass

    @property
    def SCREEN_SIZE(self):
        return tuple(self.__screen_size)

    @property
    def SCREEN_W(self):
        return int(self.SCREEN_SIZE[0])

    @property
    def SCREEN_H(self):
        return int(self.SCREEN_SIZE[1])
