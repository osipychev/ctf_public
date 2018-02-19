import time
import gym
import gym_cap

start_time = time.time()
env = gym.make("cap-v0")
observation = env.reset()
done = False
t = 0
while not done:
    action = env.action_space.sample()  # choose random action
    # action = ["S", "X", "X", "X"]
    observation, reward, done, info = env.step(action)  # feedback from environment
    env.render("human")
    t += 1
    # if not t % 100:
        # print(t, info)
    time.sleep(5)
    if t == 100000:
        break
print("--- %s seconds ---" % (time.time() - start_time))
