#!/usr/bin/env python3
import gym
import gym_cap
import numpy as np
import policy.roomba
import policy.random

# Linking Gym with Gazebo
import rospy, tf, os
import rospkg
from std_msgs.msg import *
from geometry_msgs.msg import *
from gazebo_msgs.srv import DeleteModel, SpawnModel

class CtfNode:

    def __init__(self, maxsteps=100, map_size=20, agents=["TS1","TS2","TS3","TS4","TS5","TS6","TS7","TS8",]):

        env = gym.make("cap-v0") # initialize the environment
        self.done = False
        self.steps = 0
        self.score = 0
        self.maxsteps = maxsteps

        self.observation = env.reset(map_size=map_size,
                        policy_blue=policy.random.PolicyGen(env.get_map, env.get_team_blue),
                        policy_red=policy.roomba.PolicyGen(env.get_map, env.get_team_red))
        self.env = env

        # ROS components to link with Gazebo
        rospy.init_node('cap_gazebo_node')
        self.flags = {}

        goalTopics = [str(bot)+'/goal' for bot in agents]
        flagTopics = [[str(bot)+'/flag/ready',str(bot)] for bot in agents]
        self.pubs = [rospy.Publisher(topic, Point, queue_size=10) for topic in goalTopics]
        self.subs = [rospy.Subscriber(topic, Bool, self.flagCallback, str(bot)) for topic,bot in flagTopics]

        # obs = self.get_obstacle_positions()
        # print(obs)
        #
        # rospack = rospkg.RosPack()
        # models_root = rospack.get_path('terrasentia_models')
        # obstacle_path = os.path.join(models_root,'1m_cube_obstacle/model.sdf')
        # with open(obstacle_path, "r") as f:
        #     self.obstacle_xml = f.read()

        # self.spawn_obstacles(obs)

        self.r = rospy.Rate(10) # 10hz

    def flagCallback(self, data, args):
        self.flags[args] = data.data

    def step(self):
        self.observation, self.score, self.done, _ = self.env.step()  # feedback from environment
        self.render()
        self.steps += 1

    def render(self):
        # render and sleep are not needed for score analysis
        self.env.render()

    def loop(self):
        while not self.done:
            while not self.update_gazebo_flags():
                self.r.sleep()

            print("Stepping")
            self.env.step();
            self.render()
            self.goals = self.get_agent_positions()
            self.update_gazebo_goals()
            if self.steps == self.maxsteps:
                break

    def run(self):
        while True:
            self.env.reset()
            self.loop()
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

    def update_gazebo_goals(self):
        goals = self.goals
        goal = Point()
        for i in range(0,len(goals)):
            tmpGoal = goals[i]
            goal.x = tmpGoal[0] - 10
            goal.y = tmpGoal[1] - 10
            self.pubs[i].publish(goal)
            self.r.sleep()

    def update_gazebo_flags(self):
        flags = self.flags
        isReady = all(flag==True for flag in flags.values() )
        print("isReady: ",flags)
        return isReady

    def spawn_obstacles(self, positions):

        print("Waiting for gazebo services...")
        rospy.wait_for_service("gazebo/delete_model")
        rospy.wait_for_service("gazebo/spawn_sdf_model")
        d = rospy.ServiceProxy("gazebo/delete_model", DeleteModel)
        s = rospy.ServiceProxy("gazebo/spawn_sdf_model", SpawnModel)



        pose = Pose()
        quats = tf.transformations.quaternion_from_euler(0,0,0)

        for num in xrange(0,100):
            model_name = "obstacle_{0}".format(num)
            print("Deleting model:%s", model_name)
            d(model_name)

    	for num in xrange(0,len(positions)):
            model_name   =   "obstacle_{0}".format(num)
            print("Spawning model:%s", model_name)
            pose.position.x = positions[num][0] - 10;
            pose.position.y = positions[num][1] - 10;
            pose.position.z = 0
            pose.orientation.x = quats[0]; pose.orientation.y = quats[1]; pose.orientation.z = quats[2]; pose.orientation.w = quats[3]
            model_pose   =   pose
            s(model_name, self.obstacle_xml, "", model_pose, "world")


if __name__ == '__main__':
    cf = CtfNode()
    cf.loop()
