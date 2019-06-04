import numpy as np
import random
from .const import *

class CreateMap:
    """This class generates and back-propogates a random map
    given dimension size, number of obstacles,
    and number of agents for each team"""

    @staticmethod
    def gen_map(name, dim=20, in_seed=None, rand_zones=False, np_random=None,
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

        assert map_obj is not None

        # init the seed and set new_map to zeros
        if np_random == None:
            np_random = np.random
        if not in_seed == None:
            np.random.seed(in_seed)
        new_map = np.empty([dim, dim], dtype=int)

        # zones init
        new_map[:] = TEAM2_BACKGROUND
        if rand_zones:
            sx, sy = np_random.randint(dim//2, 4*dim//5, [2])
            lx, ly = np_random.randint(0, dim - max(sx,sy)-1, [2])
            new_map[lx:lx+sx, ly:ly+sy] = TEAM1_BACKGROUND
        else:
            new_map[:,0:dim//2] = TEAM1_BACKGROUND

        # obstacles init
        num_obst = int(np.sqrt(dim))
        for i in range(num_obst):
            lx, ly = np_random.randint(0, dim, [2])
            sx, sy = np_random.randint(0, dim//5, [2]) + 1
            new_map[lx-sx:lx+sx, ly-sy:ly+sy] = OBSTACLE

        element_count = dict(zip(*np.unique(new_map, return_counts=True)))
        if element_count[TEAM1_BACKGROUND] < 1 + map_obj[0] + map_obj[1]:
            raise Exception('Cannot fit all blue object in an given map.')
        if element_count[TEAM2_BACKGROUND] < 1 + map_obj[2] + map_obj[3]:
            raise Exception('Cannot fit all red object in an given map.')

        # define location of flags
        team1_pool = np.argwhere(new_map==TEAM1_BACKGROUND).tolist()
        team2_pool = np.argwhere(new_map==TEAM2_BACKGROUND).tolist()
        random.shuffle(team1_pool)
        random.shuffle(team2_pool)

        CreateMap.populate_map(new_map, team1_pool, TEAM1_FLAG, 1)
        CreateMap.populate_map(new_map, team2_pool, TEAM2_FLAG, 1)

        # the static map is ready
        static_map = np.copy(new_map)

        CreateMap.populate_map(new_map, team1_pool, TEAM1_UGV, map_obj[0])
        CreateMap.populate_map(new_map, team1_pool, TEAM1_UAV, map_obj[1])
        CreateMap.populate_map(new_map, team2_pool, TEAM2_UGV, map_obj[2])
        CreateMap.populate_map(new_map, team2_pool, TEAM2_UAV, map_obj[3])

        # TODO: change zone for grey team to complete map
        #new_map = CreateMap.populate_map(new_map,
        #                     TEAM2_BACKGROUND, TEAM3_UGV, map_obj[4])

        #np.save('map.npy', new_map)
        return new_map, static_map
    
    @staticmethod
    def set_custom_map(new_map):
        """
        Method
            Outputs static_map when new_map is given as input.
            Addtionally the number of agents will also be
            counted
        
        Parameters
        ----------
        new_map        : numpy array
            new_map
        The necessary elements:
            ugv_1   : blue UGV
            ugv_2   : red UGV
            uav_2   : red UAV
            gray    : gray units
            
        """
        static_map = np.copy(new_map)
        element_count = dict(zip(*np.unique(new_map, return_counts=True)))
        ugv_1 = element_count.get(TEAM1_UGV, 0)
        ugv_2 = element_count.get(TEAM2_UGV, 0)
        uav_1 = element_count.get(TEAM1_UAV, 0)
        uav_2 = element_count.get(TEAM2_UAV, 0)
        gray = element_count.get(TEAM3_UGV, 0)
                    
        static_map[static_map==TEAM1_UGV] = TEAM1_BACKGROUND
        static_map[static_map==TEAM1_UAV] = TEAM1_BACKGROUND
        static_map[static_map==TEAM2_UGV] = TEAM2_BACKGROUND
        static_map[static_map==TEAM2_UAV] = TEAM2_BACKGROUND
        static_map[static_map==TEAM3_UGV] = TEAM1_BACKGROUND # subject to change
            
        # new_map becomes static_map    
        return new_map, static_map, [ugv_1, uav_1, ugv_2, uav_2, gray]

    @staticmethod
    def populate_map(new_map:np.ndarray, code_where:list, code_what:int, number:int=1):
        """
        Function
            Adds "code_what" to a random location of "code_where" at "new_map"

        Parameters
        ----------
        new_map     : 2d numpy array
            Map of the environment
        code_where  : list
            List of coordinate to put element 
        code_what   : int
            Value assigned to the random location of the map
        number      : int
            Number of element to place
        """
        if number == 0:
            return

        args = np.array(code_where[:number])
        del code_where[:number]

        new_map[args[:,0], args[:,1]] = code_what
