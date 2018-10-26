import gym
import gym_cap
import numpy as np
import policy.roomba
import policy.random

class CtfNode:

    def __init__(self, maxsteps=100):

        env = gym.make("cap-v0") # initialize the environment
        self.done = False
        self.steps = 0
        self.score = 0
        self.maxsteps = 100

        self.observation = env.reset(map_size=20,
                        policy_blue=policy.random.PolicyGen(env.get_map, env.get_team_blue),
                        policy_red=policy.roomba.PolicyGen(env.get_map, env.get_team_red))
        self.env = env

    def step(self):
        self.observation, self.score, self.done, _ = env.step()  # feedback from environment
        self.render()
        self.steps += 1

    def render(self):
        # render and sleep are not needed for score analysis
        self.env.render()

    def loop(self):
        while not self.done:
            self.env.step();
            if self.steps == self.maxsteps:
                break
    def run(self):
        self.env.reset()
        self.done = False
        print("Score: %.2f" % self.reward)

    def get_agent_positions(self):
        locations = []

        team1 = self.env.get_team_blue
        for agent in team1:
            locations.append(agent.get_loc())

        team2 = self.env.get_team_red
        for agent in team2:
            locations.append(agent.get_loc())

        return locations

    def get_flag_positions(self):
        locations = []

        for y in range(len(self.env._env)):
            for x in range(len(self.env._env[0])):
                if self.env._env[x][y] == 6:
                    locations.append([x,y])
                if self.env._env[x][y] == 7:
                    locations.append([x,y])

        return locations

    def get_obstacle_positions(self):
        locations = []

        for y in range(len(self.env._env)):
            for x in range(len(self.env._env[0])):
                if self.env._env[x][y] == 8:
                    locations.append([x,y])

        return locations
