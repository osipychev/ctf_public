import numpy as np
from .const import *

class EnemyAI:
    def __init__(self,map_only):
        #self.modes = {'patrol':1, 'moveto':2, 'explore':3, 'saveFlag':4}
        self.mode = 1
        self.map_only = map_only
        #find the zone border
        #for col in range(len(map_only[0])):
        self.border = 0
        for row in range(len(map_only)):
            if (map_only[row][0] == TEAM1_BACKGROUND and
                map_only[row+1][0] == TEAM2_BACKGROUND):
                self.border = row + 1
                break
        self.action = 0
        
    def patrol(self, agent, observation, agent_list):
        x,y = agent.get_loc()
        self.action = 0
        if y > self.border + 2:
            self.action = 0 # if below bottom line of def - go north
            if self.map_only[y-1][x] != TEAM2_BACKGROUND:
                self.action = 1
        elif y < self.border + 1:
            self.action = 2 # if above top line of def - go south
            if self.map_only[y+1][x] != TEAM2_BACKGROUND:
                self.action = 1
        elif y == self.border + 1:
            self.action = 1 # if at top line - go east
            if (x >= len(self.map_only[0])-1 or
                self.map_only[y][x+1] != TEAM2_BACKGROUND):
                self.action = 2
        elif y == self.border + 2:
            self.action = 3 # if at bottom line - go west
            if (x <= 0 or
                self.map_only[y][x-1] != TEAM2_BACKGROUND):
                self.action = 0

        return self.action
    
    def gen_random(on_map, code_where):
        dim = on_map.shape[0]
        while True:
            lx, ly = np.random.randint(0, dim, [2])
            if on_map[lx,ly] == code_where:
                break
        return lx, ly