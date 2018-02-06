##this software is developed for research purpose by Denis Osipychev
# DASLAB UIUC 2018

import numpy as np
import matplotlib.pyplot as plt

##=== Defining the refences
class TeamConst:
    RED = 10
    BLUE = 50
    GRAY = 90
    NUM_BLUE = 4
    NUM_RED = 4
    NUM_UAV = 2
    NUM_GRAY = 10
    UAV_STEP = 3
    UGV_STEP = 1
    UAV_RANGE = 4
    UGV_RANGE = 2
    
class MapConst:
    WORLD_H = 100
    WORLD_W = 100
    RED_ZONE = 15
    RED_AGENT = 20
    RED_FLAG = 10
    BLUE_ZONE = 55
    BLUE_AGENT = 60
    BLUE_FLAG = 50
    GRAY_AGENT = 95
    OBSTACLE = 100
    AERIAL_DENIAL = 90
  
##=== Environment class definition
class GridWorld(object):
        
    def __init__(self):
        self._map_only = np.zeros([MapConst.WORLD_W,MapConst.WORLD_H], dtype=int)

        #zones and obstacles init
        self._map_only[:, 0:int(MapConst.WORLD_H/2)] = MapConst.RED_ZONE
        self._map_only[:, int(MapConst.WORLD_H/2):MapConst.WORLD_H] = MapConst.BLUE_ZONE
        
        # !! hardcoded size of the map. need to change later
        for i in range(4):
            lx, ly = np.random.randint(0,100,[2])
            self._map_only[lx-10:lx+10, ly-10:ly+10] = MapConst.OBSTACLE
    
        self._map_only[np.random.randint(0,100),np.random.randint(0,int(MapConst.WORLD_H/2))] = MapConst.RED_FLAG
        self._map_only[np.random.randint(0,100),np.random.randint(int(MapConst.WORLD_H/2),MapConst.WORLD_H)] = MapConst.BLUE_FLAG
                        
        self._map_full = np.copy(self._map_only)
        self._map_red = np.copy(self._map_only)
        self._map_blue = np.copy(self._map_only)
        
    def get_map(self, team=None):
        if team == TeamConst.BLUE:
            return self._map_blue
        elif team == TeamConst.RED:
            return self._map_red
        else:
            return self._map_only
    
    def get_loc(self, x, y):
        return self._map_full[x,y]
    
    def _update_dependent_maps(self, agents):
        self._map_red = np.zeros([MapConst.WORLD_W,MapConst.WORLD_H])#np.copy(self._map_only)
        self._map_blue = np.zeros([MapConst.WORLD_W,MapConst.WORLD_H])#np.copy(self._map_only)
        for agent in agents:
            l = agent.get_loc()
            for xi in range(-agent.range,agent.range):
                for yi in range(-agent.range,agent.range):
                    locx, locy = l[0] + xi, l[1] + yi
                    locx, locy = np.clip([locx,locy],0,99) ## ! hardcoded map size. need to change later
                    if agent.get_team() == TeamConst.RED:
                        self._map_red[locx, locy] = self._map_full[locx, locy]
                    elif agent.get_team() == TeamConst.BLUE:
                        self._map_blue[locx, locy] = self._map_full[locx, locy]
                        
    def update_map(self, agents):
        temp_map = np.copy(self._map_only)
        for agent in agents:
            if agent.get_team() == TeamConst.RED:
                temp_map[agent.get_loc()] = MapConst.RED_AGENT
            elif agent.get_team() == TeamConst.BLUE: 
                temp_map[agent.get_loc()] = MapConst.BLUE_AGENT
            elif agent.get_team() == TeamConst.GRAY: 
                temp_map[agent.get_loc()] = MapConst.GRAY_AGENT
        self._map_full = temp_map
        self._update_dependent_maps(agents)
               
    def plot_all(self):
        plt.subplot(1,3,1)
        plt.title('Capture the Flag')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.imshow(self._map_full)
        
        plt.subplot(1,3,2)
        plt.title('Blue Team View')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.imshow(self._map_blue)
        
        plt.subplot(1,3,3)
        plt.title('Red Team View')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.imshow(self._map_red)
            
        plt.pause(0.5)
        #plt.show()
        #plt.gcf().clear()

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
    
##=== SIMULATION STARTS HERE

gr = GridWorld()
agents_list = []

for i in range(TeamConst.NUM_RED//2):
    l = np.random.randint(0,100,[2])
    agents_list.append(GroundVehicle(l, TeamConst.RED))
    l = np.random.randint(0,100,[2])
    agents_list.append(AerialVehicle(l, TeamConst.RED))
for i in range(TeamConst.NUM_BLUE//2):
    l = np.random.randint(0,100,[2])
    agents_list.append(GroundVehicle(l, TeamConst.BLUE))
    l = np.random.randint(0,100,[2])
    agents_list.append(AerialVehicle(l, TeamConst.BLUE))
for i in range(TeamConst.NUM_GRAY):
    l = np.random.randint(0,100,[2])
    agents_list.append(GroundVehicle(l, TeamConst.GRAY))

gr.update_map(agents_list)

fig = plt.figure(0,figsize=[15,5])

while(plt.fignum_exists(0)):
    for agent in agents_list:
        agent.move(np.random.randint(0,5))
        gr.update_map(agents_list)
    gr.plot_all()
    
    
