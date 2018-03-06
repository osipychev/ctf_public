""" this software is developed for research purpose by Denis Osipychev
 DASLAB UIUC 2018
"""

import numpy as np
np.set_printoptions(threshold=np.nan)
import matplotlib.pyplot as plt

from const import TeamConst, MapConst
from agent import Agent, GroundVehicle, AerialVehicle, GrayAgent
from gridworld import GridWorld

# SIMULATION STARTS HERE
gr = GridWorld()
agents_list = []

for i in range(TeamConst.NUM_RED//2):
    loc = np.random.randint(0, 100, [2])
    agents_list.append(GroundVehicle(loc, TeamConst.RED))
    loc = np.random.randint(0, 100, [2])
    agents_list.append(AerialVehicle(loc, TeamConst.RED))
for i in range(TeamConst.NUM_BLUE//2):
    loc = np.random.randint(0, 100, [2])
    agents_list.append(GroundVehicle(loc, TeamConst.BLUE))
    loc = np.random.randint(0, 100, [2])
    agents_list.append(AerialVehicle(loc, TeamConst.BLUE))
for i in range(TeamConst.NUM_GRAY):
    loc = np.random.randint(0, 100, [2])
    agents_list.append(GroundVehicle(loc, TeamConst.GRAY))

gr.update_map(agents_list)

#fig = plt.figure(0, figsize=[15, 5])

#while(plt.fignum_exists(0)):
for t in range(10):
    for agent in agents_list:
        agent.move(np.random.randint(0, 5))
        gr.update_map(agents_list)
    print(gr.get_map().flatten())
#    gr.plot_all()
