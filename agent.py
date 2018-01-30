from constants import Constants, Team, MapCodes

##=== agent classes
class Agent():
    
    def __init__(self, loc, team):
        try:
            self.x, self.y = loc
            self.team = team
        except:
            print("error: cannot initialize agent")
    
    def move(self,action):
        x,y = self.x, self.y
        if action == 0: 
            pass
        elif action == 1: 
            x -= 1
        elif action == 2:
            x += 1
        elif action == 3:
            y -= 1
        elif action == 4:
            y += 1
        else:
            print("error: wrong action selected")
        
        self.x = max(min(WORLD_W-1, x), 0)
        self.y = max(min(WORLD_H-1, y), 0)
            
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
        
class GrayAgent(GroundVehicle):
    
    def __init__(self,loc,team):
        Agent.__init__(self,loc,Team.GRAY)
        self.direction = [0,0]
        
    def check_complete(self):
        return self.get_loc == self.direction