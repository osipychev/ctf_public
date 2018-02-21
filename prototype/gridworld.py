import numpy as np
import matplotlib.pyplot as plt

from const import TeamConst, MapConst


class GridWorld(object):
    """    Environment class definition  """
    def __init__(self):
        self._map_only = np.zeros([MapConst.WORLD_W, MapConst.WORLD_H],
                                  dtype=int)

        # zones and obstacles init
        self._map_only[:, 0:int(MapConst.WORLD_H/2)] = MapConst.RED_ZONE
        self._map_only[
                :, int(MapConst.WORLD_H/2):MapConst.WORLD_H
                ] = MapConst.BLUE_ZONE

        # !! hardcoded size of the map. need to change later
        for i in range(4):
            lx, ly = np.random.randint(0, 100, [2])
            self._map_only[lx-10:lx+10, ly-10:ly+10] = MapConst.OBSTACLE

        self._map_only[
                np.random.randint(0, 100),
                np.random.randint(0, int(MapConst.WORLD_H/2))
                ] = MapConst.RED_FLAG
        self._map_only[
                np.random.randint(0, 100),
                np.random.randint(int(MapConst.WORLD_H/2), MapConst.WORLD_H)
                ] = MapConst.BLUE_FLAG

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
        return self._map_full[x, y]

    def _update_dependent_maps(self, agents):
        self._map_red = np.zeros([MapConst.WORLD_W, MapConst.WORLD_H])
        # np.copy(self._map_only)
        self._map_blue = np.zeros([MapConst.WORLD_W, MapConst.WORLD_H])
        # np.copy(self._map_only)
        for agent in agents:
            loc = agent.get_loc()
            for xi in range(-agent.range, agent.range):
                for yi in range(-agent.range, agent.range):
                    locx, locy = loc[0] + xi, loc[1] + yi
                    locx, locy = np.clip([locx, locy], 0, 99)
                    # ! hardcoded map size. need to change later
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
        plt.subplot(1, 3, 1)
        plt.title('Capture the Flag')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.imshow(self._map_full)

        plt.subplot(1, 3, 2)
        plt.title('Blue Team View')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.imshow(self._map_blue)

        plt.subplot(1, 3, 3)
        plt.title('Red Team View')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.imshow(self._map_red)

        plt.pause(0.5)
        # plt.show()
        # plt.gcf().clear()
