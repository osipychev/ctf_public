import numpy as np
from .const import *

class EnemyAI:
    def patrol(map_only, team2):
        #find the zone border
        #for col in range(len(map_only[0])):
        border = 0
        team_actions = []
        for row in range(len(map_only)):
            if (map_only[row][0] == TEAM1_BACKGROUND and
                map_only[row+1][0] == TEAM2_BACKGROUND):
                border = row + 1
                break

        for entity in team2:
            x,y = entity.get_loc()
            action = 0
            if y > border + 2:
                action = 0 # if below bottom line of def - go north
                if map_only[y-1][x] != TEAM2_BACKGROUND:
                    action = 1
            elif y < border + 1:
                action = 2 # if above top line of def - go south
                if map_only[y+1][x] != TEAM2_BACKGROUND:
                    action = 1
            elif y == border + 1:
                action = 1 # if at top line - go east
                if (x >= len(map_only[0])-1 or
                    map_only[y][x+1] != TEAM2_BACKGROUND):
                    action = 2
            elif y == border + 2:
                action = 3 # if at bottom line - go west
                if (x <= 0 or
                    map_only[y][x-1] != TEAM2_BACKGROUND):
                    action = 0

            team_actions.append(action)

        return team_actions
