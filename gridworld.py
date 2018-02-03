import numpy as np
import matplotlib.pyplot as plt

##=== Defining grid world constants

WORLD_H = 100
WORLD_W = 100
NUM_BLUE = 4
NUM_RED = 4
NUM_GRAY = 10

fig = plt.figure(0,figsize=[10,10])

##=== Defining the refences
class Team:
    RED = 10
    BLUE = 50
    GRAY = 90
    
class MapCodes:
    RED_ZONE = 15
    RED_AGENT = 20
    RED_FLAG = 10
    BLUE_ZONE = 55
    BLUE_AGENT = 60
    BLUE_FLAG = 50
    GRAY_AGENT = 95
    OBSTACLE = 100
    AERIAL_DENIAL = 90
    

##=== Grid World class
class GridWorld(object):
        
    def __init__(self):
        self._map_only = np.zeros([WORLD_W,WORLD_H], dtype=int)

        #zones and obstacles
        self._map_only[:,0:int(WORLD_H/2)] = MapCodes.RED_ZONE
        self._map_only[:,int(WORLD_H/2):WORLD_H] = MapCodes.BLUE_ZONE
        self._map_only[10:35,10:35] = MapCodes.OBSTACLE
        self._map_only[10:35,65:90] = MapCodes.OBSTACLE
        self._map_only[65:90,10:35] = MapCodes.OBSTACLE
        self._map_only[65:90,65:90] = MapCodes.OBSTACLE
    
        self._map_only[np.random.randint(0,100),np.random.randint(0,int(WORLD_H/2))] = MapCodes.RED_FLAG
        self._map_only[np.random.randint(0,100),np.random.randint(int(WORLD_H/2),WORLD_H)] = MapCodes.BLUE_FLAG
                        
        self._map_full = np.copy(self._map_only)
        self._map_red = np.copy(self._map_only)
        self._map_blue = np.copy(self._map_only)
        
    def get_map(self, team=None):
        if team == Team.Blue:
            return self._map_blue
        elif team == Team.Red:
            return self._map_red
        else:
            return self._map_only
    
    def get_loc(self, x, y):
        return self._map_full[x,y]
    
    def update_map(self,agents):
        temp_map = np.copy(self._map_only)
        for agent in agents:
            if agent.get_team() == Team.RED:
                temp_map[agent.get_loc()] = MapCodes.RED_AGENT
            elif agent.get_team() == Team.BLUE: 
                temp_map[agent.get_loc()] = MapCodes.BLUE_AGENT
            elif agent.get_team() == Team.GRAY: 
                temp_map[agent.get_loc()] = MapCodes.GRAY_AGENT
        self._map_full = temp_map
        
        self._map_red = np.copy(self._map_only)
        self._map_blue = np.copy(self._map_only)
        for agent in agents:
            l = agent.get_loc()
            if agent.get_team() == Team.RED:
                for xi in range(-agent.range,agent.range):
                    for yi in range(-agent.range,agent.range):
                        locx, locy = l[0] + xi, l[1] + yi
                        try:
                            self._map_red[locx, locy] = self._map_full[locx, locy]
                        except:
                            print("outside the map")
            
            
        return temp_map
                            
               
    def plot_all(self, team=None):
        if team == Team.BLUE:
            plt.imshow(self._map_blue)
        elif team == Team.RED:
            plt.imshow(self._map_red)
        else:
            plt.imshow(self._map_full)
        plt.pause(0.5)
        #plt.show()
        plt.gcf().clear()


##=== agent classes
class Agent():
    
    def __init__(self, loc, team):
        try:
            self.x, self.y = loc
            self.team = team
            self.step = 1
            self.range = 2
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
        self.step = 3
        self.range = 4
        
class GrayAgent(GroundVehicle):
    
    def __init__(self,loc,team):
        Agent.__init__(self,loc,Team.GRAY)
        self.direction = [0,0]
        
    def check_complete(self):
        return self.get_loc == self.direction
    
##=== CIMULATION STARTS HERE

gr = GridWorld()
blue_team = []
red_team = []
gray_team = []
agents_list = []

red_team_obs = []
blue_team_obs = []

for i in range(NUM_RED//2):
    l = np.random.randint(0,100,[2])
    red_team.append(GroundVehicle(l, Team.RED))
    l = np.random.randint(0,100,[2])
    red_team.append(AerialVehicle(l, Team.RED))
for i in range(NUM_BLUE//2):
    l = np.random.randint(0,100,[2])
    red_team.append(GroundVehicle(l, Team.BLUE))
    l = np.random.randint(0,100,[2])
    red_team.append(AerialVehicle(l, Team.BLUE))
for i in range(NUM_GRAY):
    l = np.random.randint(0,100,[2])
    gray_team.append(GroundVehicle(l, Team.GRAY))

agents_list.extend(red_team)
agents_list.extend(blue_team)
agents_list.extend(gray_team)
gr.update_map(agents_list)

for i in range(1000):
    for agent in agents_list:
        agent.move(np.random.randint(0,5))
        gr.update_map(agents_list)
    gr.plot_all(Team.RED)
