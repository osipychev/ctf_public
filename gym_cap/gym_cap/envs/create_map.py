import numpy as np
from .const import *

class CreateMap:
    """This class generates a random map
    given dimension size, number of obstacles,
    and number of agents for each team"""

    @staticmethod
    def gen_map(name, dim=20, in_seed=None, rand_zones=False,
                map_obj=[NUM_BLUE, NUM_UAV, NUM_RED, NUM_UAV, NUM_GRAY]):
        """
        Method

        Parameters
        ----------
        name        : TODO
            Not used
        dim         : int
            Size of the map
        in_seed     : int
            Random seed between 0 and 2**32
        rand_zones  : bool
            True if zones are defined random
        map_obj     : list
            The necessary elements to build the map
            0   : blue UGV
            1   : blue UAV
            2   : red UGV
            3   : red UAV
            4   : gray units
        """

        # init the seed and set new_map to zeros
        if not in_seed == None:
            np.random.seed(in_seed)
        new_map = np.zeros([dim, dim], dtype=int)

        # zones init
        new_map[:,:] = TEAM2_BACKGROUND
        if rand_zones:
            sx, sy = np.random.randint(dim//2, 4*dim//5, [2])
            lx, ly = np.random.randint(0, dim - max(sx,sy)-1, [2])
            new_map[lx:lx+sx, ly:ly+sy] = TEAM1_BACKGROUND
        else:
            new_map[:,0:dim//2] = TEAM1_BACKGROUND

        # obstacles init
        num_obst = int(np.sqrt(dim))
        for i in range(num_obst):
            lx, ly = np.random.randint(0, dim, [2])
            sx, sy = np.random.randint(0, dim//5, [2]) + 1
            new_map[lx-sx:lx+sx, ly-sy:ly+sy] = OBSTACLE

        # define location of flags
        new_map = CreateMap.populate_map(new_map,
                             TEAM1_BACKGROUND, TEAM1_FLAG)
        new_map = CreateMap.populate_map(new_map,
                             TEAM2_BACKGROUND, TEAM2_FLAG)

        # the static map is ready
        static_map = np.copy(new_map)

        for i in range(map_obj[0]):
            new_map = CreateMap.populate_map(new_map,
                                 TEAM1_BACKGROUND, TEAM1_UGV)
        for i in range(map_obj[1]):
            new_map = CreateMap.populate_map(new_map,
                                 TEAM1_BACKGROUND, TEAM1_UAV)
        for i in range(map_obj[2]):
            new_map = CreateMap.populate_map(new_map,
                                 TEAM2_BACKGROUND, TEAM2_UGV)
        for i in range(map_obj[3]):
            new_map = CreateMap.populate_map(new_map,
                                 TEAM2_BACKGROUND, TEAM2_UAV)

        # TODO: change zone for grey team to complete map
        for i in range(map_obj[4]):
            new_map = CreateMap.populate_map(new_map,
                                 TEAM2_BACKGROUND, TEAM3_UGV)

        #np.save('map.npy', new_map)
        return new_map, static_map

    @staticmethod
    def populate_map(new_map, code_where, code_what):
        """
        Function
            Adds "code_what" to a random location of "code_where" at "new_map"

        Parameters
        ----------
        new_map     : 2d numpy array
            Map of the environment
        code_where  : int
            Code of the territory that is being populated
        code_what   : int
            Value assigned to the random location of the map
        """
        dimx, dimy = new_map.shape
        while True:
            lx = np.random.randint(0, dimx)
            ly = np.random.randint(0, dimy)
            if new_map[lx,ly] == code_where:
                break
        new_map[lx,ly] = code_what
        return new_map
