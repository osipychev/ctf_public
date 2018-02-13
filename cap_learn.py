import time
import gym
import gym_cap

start_time = time.time()
env = gym.make("cap-v0")
observation = env.reset()
done = False
t = 0
while not done:
    env.render("human")
    # action = env.action_space.sample()  # choose random action
    action = ["N", "X", "X", "X"]
    observation, reward, done, info = env.step(action)  # feedback from environment
    t += 1
    # if not t % 100:
        # print(t, info)
    if t == 100000:
        break
print("--- %s seconds ---" % (time.time() - start_time))
