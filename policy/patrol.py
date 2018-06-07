#import numpy as np

class PolicyGen:
    def __init__(self,map_only):
        
        self.map_only = map_only
        self.heading_right = [True, True, True, True]
        
    def gen_action(self, agent_list, observation, map_only=None):
        
        action_out = []
        if map_only is not None: self.map_only = map_only
        
        for idx,agent in enumerate(agent_list):
            a = self.__patrol(agent, idx, observation)
            action_out.append(a)
        
        return action_out

    def __patrol(self, agent, idx, obs):
        x,y = agent.get_loc()
        action = 0
        
        #approach the boarder
        if (y > len(self.map_only[0])/2 + 1 and 
            self.map_only[x][y-1] == self.map_only[x][y]):
            action = 1
        elif (y < len(self.map_only[0])/2 - 1 and
            self.map_only[x][y+1] == self.map_only[x][y]):
            action = 3
        
        #patrol along the boarder
        else:
            if (x <= 0 or x >= len(self.map_only)-1):
                self.heading_right[idx] = not self.heading_right[idx]
                
            #if in the map and have free space at right - go right
            if (self.heading_right[idx] and 
                obs[x+1][y] == self.map_only[x][y]): 
                action = 2
            #if in the map and have free space at left - go left
            elif (not self.heading_right[idx] and 
                  obs[x-1][y] == self.map_only[x][y]): 
                action = 4
            else:
                self.heading_right[idx] = not self.heading_right[idx]
                
        return action