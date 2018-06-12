"""Patrolling agents policy generator.

This module demonstrates an example of a simple heuristic policy generator
for Capture the Flag environment.
    http://github.com/osipychev/missionplanner/

DOs/Denis Osipychev
    http://www.denisos.com

"""

#import numpy as np


class PolicyGen:
    """Policy generator class for CtF env.
    
    This class can be used as a template for policy generator.
    Designed to summon an AI logic for the team of units.
    
    Methods:
        gen_action: Required method to generate a list of actions.
        patrol: Private method to control a single unit.
    """
    
    def __init__(self, free_map, agent_list):
        """Constuctor for policy class.
        
        Patrolling policy provides the actions for the team of units that
        command units to approach the boarder between friendly and enemy
        zones and patrol along it.
        
        Args:
            free_map (np.array): 2d map of static environment.
            agent_list (list): list of all friendly units.
        """
        self.free_map = free_map 
        self.heading_right = [True] * len(agent_list) #: Attr to track directions.
        
    def gen_action(self, agent_list, observation, free_map=None):
        """Action generation method.
        
        This is a required method that generates list of actions corresponding 
        to the list of units. 
        
        Args:
            agent_list (list): list of all friendly units.
            observation (np.array): 2d map of partially observable map.
            free_map (np.array): 2d map of static environment (optional).
            
        Returns:
            action_out (list): list of integers as actions selected for team.
        """
        action_out = []
        
        if free_map is not None: self.free_map = free_map
        
        for idx,agent in enumerate(agent_list):
            a = self.patrol(agent, idx, observation)
            action_out.append(a)
        
        return action_out

    def patrol(self, agent, index, obs):
        """Generate 1 action for given agent object."""
        x,y = agent.get_loc()
        action = 0
        
        #approach the boarder.
        if (y > len(self.free_map[0])/2 and 
            self.free_map[x][y-1] == self.free_map[x][y]):
            action = 1
        elif (y < len(self.free_map[0])/2 - 1 and
            self.free_map[x][y+1] == self.free_map[x][y]):
            action = 3
        
        #patrol along the boarder.
        else:
            if (x <= 0 or x >= len(self.free_map)-1):
                self.heading_right[index] = not self.heading_right[index]
                
            #if in the map and have free space at right - go right.
            if (self.heading_right[index] and 
                x+1 < len(self.free_map) and
                obs[x+1][y] == self.free_map[x][y]): 
                action = 2
            #if in the map and have free space at left - go left.
            elif (not self.heading_right[index] and
                  x > 0 and
                  obs[x-1][y] == self.free_map[x][y]): 
                action = 4
            #otherwise - turn around.
            else:
                self.heading_right[index] = not self.heading_right[index]
                
        return action