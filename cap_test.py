import time
import gym
import gym_cap
import numpy as np

# the modules that you can use to generate the policy.
import policy.patrol 
import policy.random

start_time = time.time()
env = gym.make("cap-v0") # initialize the environment

done = False
t = 0
total_score = 0

# reset the environment and select the policies for each of the team
observation = env.reset(map_size=20,
                        render_mode="env",
                        policy_blue=policy.patrol.PolicyGen(env.get_map, env.get_team_blue),
                        policy_red=policy.random.PolicyGen(env.get_map, env.get_team_red))

while True:
    while not done:
        
        #you are free to select a random action
        # or generate an action using the policy
        # or select an action manually
        # and the apply the selected action to blue team
        # or use the policy selected and provided in env.reset 
        #action = env.action_space.sample()  # choose random action
        #action = policy_blue.gen_action(env.team1,observation,map_only=env.team_home)
        #action = [0, 0, 0, 0]
        #observation, reward, done, info = env.step(action)
        
        observation, reward, done, info = env.step()  # feedback from environment
        
        # render and sleep are not needed for score analysis
        env.render(mode="fast")
        time.sleep(.05)
        
        t += 1
        if t == 100000:
            break
        
    total_score += reward
    env.reset()
    done = False
    print("Total time: %s s, score: %s" % ((time.time() - start_time),total_score))

