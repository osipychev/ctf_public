#import numpy as np
#import matplotlib.pyplot as plt

from const import TeamConst, MapConst 

##=== agent class definitions
class Agent():
    
    def __init__(self, loc, team):
        try:
            self.x, self.y = loc
            self.team = team
            self.step = TeamConst.UGV_STEP
            self.range = TeamConst.UGV_RANGE 
        except:
            print("error: cannot initialize agent")
    
    def move(self,action):
        x,y = self.x, self.y
        if action == 0: 
            pass
        elif action == 1: 
            x -= self.step
        elif action == 2:
            x += self.step
        elif action == 3:
            y -= self.step
        elif action == 4:
            y += self.step
        else:
            print("error: wrong action selected")
        
        self.x = max(min(MapConst.WORLD_W-1, x), 0)
        self.y = max(min(MapConst.WORLD_H-1, y), 0)
            
    def get_loc(self):
        return self.x, self.y
    
    def get_team(self):
        return self.team
            
    def report_loc(self):
        print("report: position x:%d, y:%d" % (self.x,self.y))
            

class GroundVehicle(Agent):
    
    def __init__(self,loc,team):
        Agent.__init__(self,loc,team)       
        
        
class AerialVehicle(Agent):
        
    def __init__(self,loc,team):
        Agent.__init__(self,loc,team)
        self.step = TeamConst.UAV_STEP
        self.range = TeamConst.UAV_RANGE
        
        
class GrayAgent(GroundVehicle):
    
    def __init__(self,loc,team):
        Agent.__init__(self,loc,TeamConst.GRAY)
        self.direction = [0,0] 
        ## ! not used for now
    def check_complete(self):
        return self.get_loc == self.direction