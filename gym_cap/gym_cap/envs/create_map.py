import numpy as np
from .const import *

class CreateMap:
    """This class generates a random map
    given dimension size, number of obstacles,
    and number of agents for each team"""

    def gen_map(name, dim=20, in_seed=None, map_obj=[4, NUM_BLUE, NUM_UAV, NUM_RED, NUM_UAV, 0]):
        """
        0 <= in_seed <= 2**32

        Parameters
        ----------
        name    : TODO
            TODO
        dim     : int
            Size of the map
        map_obj : list
            The necessary elements to build the map
            0   : obstacles
            1   : player UGV
            2   : player UAV
            3   : enemy UGV
            4   : enemy UAV
            5   : gray units
        """
        if not in_seed == None:
            np.random.seed(in_seed)
        new_map = np.zeros([dim, dim], dtype=int)

        # zones and obstacles init
        new_map[:, 0:dim//2] = TEAM1_BACKGROUND
        new_map[:, dim//2:dim] = TEAM2_BACKGROUND

        for i in range(map_obj[0]):
            lx, ly = np.random.randint(0, dim, [2])
            sx, sy = np.random.randint(0, dim//5, [2]) + 1
            new_map[lx-sx:lx+sx, ly-sy:ly+sy] = OBSTACLE

        # define location of flags
        new_map = CreateMap.gen_random(new_map,
                             TEAM1_BACKGROUND, TEAM1_FLAG)
        new_map = CreateMap.gen_random(new_map,
                             TEAM2_BACKGROUND, TEAM2_FLAG)

        for i in range(map_obj[1]):
            new_map = CreateMap.gen_random(new_map,
                                 TEAM1_BACKGROUND, TEAM1_UGV)
        for i in range(map_obj[3]):
            new_map = CreateMap.gen_random(new_map,
                                 TEAM2_BACKGROUND, TEAM2_UGV)
        for i in range(map_obj[2]):
            new_map = CreateMap.gen_random(new_map,
                                 TEAM1_BACKGROUND, TEAM1_UAV)
        for i in range(map_obj[4]):
            new_map = CreateMap.gen_random(new_map,
                                 TEAM2_BACKGROUND, TEAM2_UAV)

        #np.save('map.npy', new_map)
        return new_map

    def gen_random(new_map, code_where, code_what):
        dim = new_map.shape[0]
        while True:
            lx, ly = np.random.randint(0, dim, [2])
            if new_map[lx,ly] == code_where:
                break
        new_map[lx,ly] = code_what
        return new_map
