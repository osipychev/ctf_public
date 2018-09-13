"""Simple agents policy generator.

This module demonstrates an example of a simple heuristic policy generator
for Capture the Flag environment.
    http://github.com/osipychev/missionplanner/

DOs/Denis Osipychev
    http://www.denisos.com

Last Modified : 8/30/18
By : Seung Hyun Kim
"""

import numpy as np
from collections import defaultdict


class PolicyGen:
    """Policy generator class for CtF env.

    This class can be used as a template for policy generator.
    Designed to summon an AI logic for the team of units.

    Methods:
        gen_action: Required method to generate a list of actions.
        policy: Method to determine the action based on observation for a single unit
        scan : Method that returns the dictionary of object around the agent

    Variables:
        exploration : exploration rate
        previous_move : variable to save previous action
    """

    def __init__(self, free_map, agent_list):
        """Constuctor for policy class.

        This class can be used as a template for policy generator.

        Args:
            free_map (np.array): 2d map of static environment.
            agent_list (list): list of all friendly units.
        """
        self.random = np.random

        # Constants
        self.exploration = 0.15

        # Initialize
        self.previous_move = self.random.randint(0, 5, len(agent_list)).tolist()

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

        for idx, agent in enumerate(agent_list):
            action = self.policy(agent,observation, idx)
            action_out.append(action)
            self.previous_move[idx] = action # save previous action

        return action_out

    def policy(self, agent, obs, agent_id):
        """ Policy

        This method generate an action for given agent.
        Agent is given with limited vision of a field.
        This method provides simple protocol of movement based on the agent's location and it's vision.

        Protocol :
            1. Deterministic situation (in order of priority) :
                - Encountered Enemy :
                    - Run Away
                - Flag Found :
                    - Run towards the flag
                - Wall :
                    - Change the direction
            2. Non-deterministic situation :
                - Move in the previous direction (straight forward). (85%)
                - Move in the random direction (15% exploration rate)
        """

        # Expand the observation with 3-thickness wall
        # - in order to avoid dealing with the boundary
        #print(obs)
        obsx, obsy = obs.shape
        _obs = np.ones((obsx+6, obsy+6)) * 8
        _obs[3:3+obsx, 3:3+obsy] = obs
        obs = _obs


        # Initialize Variables
        x, y = agent.get_loc()
        x += 3
        y += 3
        view = obs[x-2:x+3, y-2:y+3] # limited view for the agent
        action = 0

        # Obtain information based on the vision
        field = self.scan(view)
        elements = field.keys()

        # Checking obstacle
        dir_x = [0, 0, 1, 0, -1] # dx for [stay, up, right, down, left]
        dir_y = [0,-1, 0, 1,  0] # dy for [stay, up, right, down ,left]
        is_possible_to_move = lambda d: obs[x+dir_x[d]][y+dir_y[d]] not in [8,4]

        # Protocol
        if 2 in elements: # Enemy in the vision
            opposite_move = [0, 3, 4, 1, 2]
            action = opposite_move[self.previous_move[agent_id]]
        elif 6 in elements: # Flag Found
            # move towards the flag
            fx, fy = field[6][0] # flag location (coord. of 'view')
            if fy > 2: # move down
                action = 3
            elif fy < 2: # move up
                action = 1
            elif fx > 2: # move left
                action = 2
            elif fx < 2: # move right
                action = 4
        elif not is_possible_to_move(self.previous_move[agent_id]): # Wall or other obstacle
            action_pool = []
            for movement in range(5):
                if is_possible_to_move(movement):
                    action_pool.append(movement)
            action = np.random.choice(action_pool) # pick from possible movements
        else: # Non-deterministic situation
            if np.random.random() <= self.exploration: # Exploration
                action = np.random.randint(1,5)
            else: # Previous Move (go straight!)
                action = self.previous_move[agent_id]

        return action

    def scan(self, view):
        """
        This function returns the dictionary of locations for each element by its type.
            key : field element (int)
            value : list of element's coordinate ( (x,y) tuple )
        """

        objects = defaultdict(list)
        dx, dy = len(view), len(view[0])
        for i in range(dx):
            for j in range(dy):
                objects[view[i][j]].append((i,j))

        return objects
