import time

import gym
import gym_cap
import numpy as np

start_time = time.time()
env = gym.make("cap-v0")
done = False
t = 0
env.reset(map_size=20, mode="human_blue", in_seed=4, render_mode="obs")

while True:
    while not done:
        action = env.action_space.sample()  # choose random action
        # action = [0, 0, 0]
        # action = (4)*(5**0) \
        # +(4)*(5**1) \
        # +(4)*(5**2) \
        # +(4)*(5**3) \
        # +(4)*(5**4) \
        # +(4)*(5**5)
        suggestions = [[0, 0, 0, 1, 0],
                       [0, 0, 1, 0, 0],
                       [0, 1, 0, 0, 0],
                       [1, 0, 0, 0, 0]]
        observation, reward, done, info = env.step(action, suggestions)  # feedback from environment
        # obs, obs2,  or env

        # for agent in env.team1:
        # lx,ly = agent.get_loc()
        # # print("my loc:",lx,",",ly,", type:",observation[lx][ly])
        # small_observation = []
        # for x in range(lx-agent.range, lx+agent.range+1):
        # for y in range(ly-agent.range, ly+agent.range+1):
        # if (x<0 or y<0 or x>19 or y>19):
        # small_observation.append(-1)
        # else:
        # small_observation.append(observation[x][y])
        # small_observation = np.array(small_observation).reshape(2*agent.range+1,2*agent.range+1)
        # # print(small_observation)

        # black_line = np.array([[-2]*len(env._env[0])])
        # obs = np.concatenate((observation, black_line, env._env))
        # env.cap_view.update_env(obs)

        env.render()
        # t += 1
        # if not t % 100:
        # print(t, info)
        time.sleep(.05)
        if t == 100000:
            break
    env.reset(map_size=20, mode="human_blue", in_seed=4, render_mode="obs")
    done = False

# print("--- %s seconds ---" % (time.time() - start_time))
