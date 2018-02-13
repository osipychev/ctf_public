import pygame
import random
import numpy as np
import os

TILE_DICT = {-1 : (200, 200, 200),
             0 : (0, 0, 120),
             1 : (120, 0, 0),
             2 : (0, 0, 255),
             3 : (255, 0, 0),
             4 : (0, 255, 255),
             5 : (255, 255, 0),
             6 : (120, 120, 120)}

QUIT = 12

class CaptureView2D:
    def __init__(self, game_name="Capture the Flag", screen_size=(600, 600)):

        # PyGame configurations
        pygame.init()
        pygame.display.set_caption(game_name)
        self.clock = pygame.time.Clock()

        # to show the right and bottom border
        #TODO making white screen flash
        self.screen = pygame.display.set_mode(screen_size)
        self.__screen_size = screen_size

    def update_env(self, env):
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
                cur_color = TILE_DICT[env[row][col]]
                pygame.draw.rect(self.screen, cur_color, (col*tile_w, row*tile_h, tile_w, tile_h))
        pygame.display.update()


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
