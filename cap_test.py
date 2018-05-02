import time
import gym
import gym_cap
import numpy as np

start_time = time.time()
env = gym.make("cap-v0")
#observation = env.reset(0)
done = False
t = 0

env.reset()
while not done:
    action = env.action_space.sample()  # choose random action
    
    observation, reward, done, info = env.step(action, "random")  # feedback from environment
    #obs, obs2,  or env
    
    ### build a small observation for each unit separately
    
    for agent in env.team1:
        lx,ly = agent.get_loc()
        print("my loc:",lx,",",ly,", type:",observation[lx][ly])
        small_observation = []
        for x in range(lx-agent.range, lx+agent.range+1):
            for y in range(ly-agent.range, ly+agent.range+1):
                if (x<0 or y<0 or x>19 or y>19):
                    small_observation.append(-1)
                else:
                    small_observation.append(observation[x][y])
        small_observation = np.array(small_observation).reshape(2*agent.range+1,2*agent.range+1)
        print(small_observation)        
        
    obs = np.concatenate((observation,env._env))
    print(obs)
    env.cap_view.update_env(obs)
#        time.sleep(0.5)
    
#    env.render(mode="env")
    t += 1
    # if not t % 100:
        # print(t, info)
    time.sleep(0.5)
    # print(reward)
    if t == 100000:
        break
print("--- %s seconds ---" % (time.time() - start_time))
