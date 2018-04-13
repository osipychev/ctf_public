import pygame
import random
import numpy as np
import os
from .const import *
from pandas import *

QUIT = 12

class CaptureView2D:
    def __init__(self, game_name="Capture the Flag", screen_size=(600, 600)):

        # PyGame configurations
        pygame.init()
        pygame.display.set_caption(game_name)
        self.clock = pygame.time.Clock()

        # to show the right and bottom border
        self.screen = None
        self.__screen_size = screen_size

    def update_env(self, env):
        if self.screen == None:
            self.screen = pygame.display.set_mode(self.__screen_size)
        tile_w = self.SCREEN_W/len(env)
        tile_h = self.SCREEN_H/len(env[0])
        map_h = len(env[0])
        map_w = len(env)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()

        for row in range(map_h):
            for col in range(map_w):
                cur_color = COLOR_DICT[env[row][col]]
                if env[row][col] == TEAM1_UAV or env[row][col] == TEAM2_UAV:
                    pygame.draw.ellipse(self.screen, cur_color, [col*tile_w, row*tile_h, tile_w, tile_h])
                else:
                    pygame.draw.rect(self.screen, cur_color, (col*tile_w, row*tile_h, tile_w, tile_h))
        pygame.display.update()

    def human_move(self, env, team2):
        moves_recorded = 0
        human_move_list = [0]*(NUM_BLUE+NUM_UAV)
        tile_w = self.SCREEN_W/len(env)
        tile_h = self.SCREEN_H/len(env[0])
        map_h = len(env[0])
        map_w = len(env)
        selected = (0, 0)
        isSelected = -1
        while moves_recorded < NUM_BLUE+NUM_UAV:
            ev = pygame.event.get()

            for event in ev:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Mouse button release event
                if event.type == pygame.MOUSEBUTTONUP:
                    col = int(mouse_x/tile_w)
                    row = int(mouse_y/tile_h)
                    # Selected a unit
                    if env[row][col] == TEAM2_UAV:
                        if isSelected >= 0:
                            if env[selected[0]][selected[1]] == TEAM2_UAV:
                                pygame.draw.ellipse(self.screen, COLOR_DICT[TEAM2_UAV],\
                                                    [selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h])
                            elif env[selected[0]][selected[1]] == TEAM2_UGV:
                                pygame.draw.rect(self.screen, COLOR_DICT[TEAM2_UGV],\
                                                 [selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h])
                        pygame.draw.ellipse(self.screen, COLOR_DICT[SELECTED], [col*tile_w, row*tile_h, tile_w, tile_h])
                        selected = (row, col)
                        # Determine which unit is selected
                        for i in range(len(team2)):
                            x, y = team2[i].get_loc()
                            if x == selected[1] and y == selected[0]:
                                isSelected = i
                    elif env[row][col] == TEAM2_UGV:
                        if isSelected >= 0 and selected[0] != row and selected[1] != col:
                            if env[selected[0]][selected[1]] == TEAM2_UAV:
                                pygame.draw.ellipse(self.screen, COLOR_DICT[TEAM2_UAV],\
                                                    [selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h])
                            elif env[selected[0]][selected[1]] == TEAM2_UGV:
                                pygame.draw.rect(self.screen, COLOR_DICT[TEAM2_UGV],\
                                                    [selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h])
                        pygame.draw.rect(self.screen, COLOR_DICT[SELECTED], (col*tile_w, row*tile_h, tile_w, tile_h))
                        selected = (row, col)
                        # Determine which unit is selected
                        for i in range(len(team2)):
                            x, y = team2[i].get_loc()
                            if x == selected[1] and y == selected[0]:
                                isSelected = i
                    # Moving unit up
                    elif row < selected[0] and col == selected[1] and isSelected >= 0:
                        human_move_list[isSelected] = 0
                        moves_recorded+=1
                        if env[selected[0]][selected[1]] == TEAM2_UGV:
                            pygame.draw.rect(self.screen, COLOR_DICT[COMPLETED],\
                                             (selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h))
                        elif env[selected[0]][selected[1]] == TEAM2_UAV:
                                pygame.draw.ellipse(self.screen, COLOR_DICT[COMPLETED],\
                                                    [selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h])
                    # Moving unit down
                    elif row > selected[0] and col == selected[1] and isSelected >= 0:
                        human_move_list[isSelected] = 2
                        moves_recorded+=1
                        if env[selected[0]][selected[1]] == TEAM2_UGV:
                            pygame.draw.rect(self.screen, COLOR_DICT[COMPLETED],\
                                             (selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h))
                        elif env[selected[0]][selected[1]] == TEAM2_UAV:
                                pygame.draw.ellipse(self.screen, COLOR_DICT[COMPLETED],\
                                                    [selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h])
                    # Moving unit east
                    elif row == selected[0] and col > selected[1] and isSelected >= 0:
                        human_move_list[isSelected] = 1
                        moves_recorded+=1
                        if env[selected[0]][selected[1]] == TEAM2_UGV:
                            pygame.draw.rect(self.screen, COLOR_DICT[COMPLETED],\
                                             (selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h))
                        elif env[selected[0]][selected[1]] == TEAM2_UAV:
                                pygame.draw.ellipse(self.screen, COLOR_DICT[COMPLETED],\
                                                    [selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h])
                    # Moving unit up
                    elif row == selected[0] and col < selected[1] and isSelected >= 0:
                        human_move_list[isSelected] = 3
                        moves_recorded+=1
                        if env[selected[0]][selected[1]] == TEAM2_UGV:
                            pygame.draw.rect(self.screen, COLOR_DICT[COMPLETED],\
                                             (selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h))
                        elif env[selected[0]][selected[1]] == TEAM2_UAV:
                                pygame.draw.ellipse(self.screen, COLOR_DICT[COMPLETED],\
                                                    [selected[1]*tile_w, selected[0]*tile_h, tile_w, tile_h])
                    pygame.display.update()
        return human_move_list



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
