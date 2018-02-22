import numpy as np
from .const import TeamConst, MapConst

class CreateMap:
    """This class generates a random map
    given dimension size, number of obstacles,
    and number of agents for each team"""

    def gen_map(name, dim=20, n_obst=4, n_agents=4):
        new_map = np.zeros([dim, dim], dtype=int)

        # zones and obstacles init
        new_map[:, 0:dim//2] = MapConst.TEAM1_BACKGROUND
        new_map[:, dim//2:dim] = MapConst.TEAM2_BACKGROUND

        for i in range(n_obst):
            lx, ly = np.random.randint(0, dim, [2])
            sx, sy = np.random.randint(0, dim//5, [2]) + 1
            new_map[lx-sx:lx+sx, ly-sy:ly+sy] = MapConst.OBSTACLE

        # define location of flags
        new_map = CreateMap.gen_random(new_map,
                             MapConst.TEAM1_BACKGROUND, MapConst.TEAM1_FLAG)
        new_map = CreateMap.gen_random(new_map,
                             MapConst.TEAM2_BACKGROUND, MapConst.TEAM2_FLAG)

        for i in range(n_agents):
            new_map = CreateMap.gen_random(new_map,
                                 MapConst.TEAM1_BACKGROUND, MapConst.TEAM1_ENTITY)
            new_map = CreateMap.gen_random(new_map,
                                 MapConst.TEAM2_BACKGROUND, MapConst.TEAM2_ENTITY)

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

