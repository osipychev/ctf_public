import time
import gym
import gym_cap

start_time = time.time()
env = gym.make("cap-v0")
#observation = env.reset(0)
done = False
t = 0

while True:
    while not done:
        # action = env.action_space.sample()  # choose random action
        action = (4)*(5**0)+(4)*(5**1)+(4)*(5**2)+(4)*(5**3)+(4)*(5**4)+(4)*(5**5)
        observation, reward, done, info = env.step(action, "random")  # feedback from environment
        #obs, obs2,  or env
        env.render(mode="env")
        t += 1
        # if not t % 100:
            # print(t, info)
        time.sleep(.25)
        # print(reward)
        if t == 100000:
            break
    env.reset()
    done = False
print("--- %s seconds ---" % (time.time() - start_time))
