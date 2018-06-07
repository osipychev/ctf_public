import time
import gym
import gym_cap
import numpy as np

import policy.patrol # the module that you can use to generate the policy

start_time = time.time()
env = gym.make("cap-v0")


policy_blue = policy.patrol.PolicyGen(env.team_home)

done = False
t = 0

observation = env.reset(map_size=20, mode="random")

while True:
    while not done:
        #action = env.action_space.sample()  # choose random action
        
        action = policy_blue.gen_action(env.team1,observation,map_only=env.team_home)
        observation, reward, done, info = env.step(action)  # feedback from environment
        env.render(mode="obs")
        
        t += 1
        time.sleep(.05)
        if t == 100000:
            break
    
    env.reset()
    done = False
    print("--- %s seconds ---" % (time.time() - start_time))
