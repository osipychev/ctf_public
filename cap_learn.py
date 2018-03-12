import threading
import multiprocessing
import time
import os
import tensorflow as tf
import numpy as np
import tensorflow.contrib.slim as slim
import matplotlib.pyplot as plt
import scipy.signal

from random import choice
import gym
import gym_cap

#HYPER PARAMETERS
env_ver = "v1"
gamma = .99
load_model = False
model_path = './model'


class AC_network():
    def __init__(self, s_size, a_size, scope, trainer):
        with tf.variable_scope(scope):
            #Input and visual encoding layers
            self.inputs = tf.placeholder(shape=[None, s_size], dtype=tf.float32)
            self.imageIn = tf.reshape(self.inputs, shape[-1, a_size**.5, a_size**.5, 1])
            self.conv1 = slim.conv2d(activation_fn=tf.nn.elu, \
                                     inputs=self.imageIn, num_outputs=16, \
                                     kernel_size=[8, 8], stride=[4, 4], padding='VALID')
            self.conv2 = slim.conv2d(activation_fn=tf.nn.elu, \
                                     inputs=self.conv1, num_outputs=32, \
                                     kernel_size=[4, 4], stride=[2, 2], padding='VALID')
            hidden = slim.fully_connected(slim.flatten(self.conv2), num_outputs=256, \
                                          activation_fn=tf.nn.elu)

            #Recurrent network for temporal dependencies
            lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(256, state_is_tuple=True)
            c_init = np.zeros((1, lstm_cell.state_size.c), np.float32)
            h_init = np.zeros((1, lstm_cell.state_size.h), np.float32)
            self.state_init = [c_init, h_init]
            c_in = tf.placeholder(tf.float32, [1, lstm_cell.state_size.c])
            h_in = tf.placeholder(tf.float32, [1, lstm_cell.state_size.h])
            self.state_in = (c_in, h_in)
            rnn_in = tf.expand_dims(hidden, [0])
            step_size = tf.shape(self.imageIn)[:1]
            state_in = tf.nn.rnn_cell.LSTMstateTuple(c_in, h_in)
            lstm_outputs, lstm_state = tf.nn.dynamic_rnn( \
                lstm_cell, rnn_in, initial_state=state_in, sequence_length=step_size, \
                time_major=False)
            lstm_c, lstm_h = lstm_state
            self.state_out = (lstm_c[:1, :], lstm_h[:1, :])
            rnn_out = tf.reshape(lstm_outputs, [-1, 256])

            #Output layers for policy and value estimations
            self.policy = slim.fully_connected(rnn_out, a_size, \
                activation_fn=tf.nn.softmax, \
                weights_initializer=normalized_columns_initializer(0.01), \
                biases_initializer=None)
            self.value = slim.fully_connected(rnn_out, 1, \
                activation_fn=None, \
                weights_initializer=normalized_columns_initializer(1.0), \
                biases_initializer=None)

        if scope != 'global':
            self.actions = tf.placeholder(shape=[None], dtype=tf.int32)
            self.actions_onehot = tf.one_hot(self.actions, a_size, dtype=tf.float32)
            self.target_v = tf.placeholder(shape=[None], dtype=tf.float32)
            self.advantages = tf.placeholder(shape=[None], dtype=tf.float32)

            self.responsible_outputs = tf.reduce_sum(self.policy * self.actions_onehot, [1])

            #Loss functions
            self.value_loss = 0.5*tf.reduce_sum(tf.square(self.target_v - \
                                                          tf.reshape(self.value, [-1])))
            self.entropy = -tf.reduce_sum(self.policy * tf.log(self.policy))
            self.policy_loss = -tf.reduce_sum(tf.log(self.responsible_outputs)*self.advantages)
            self.loss = 0.5 * self.value_loss + self.policy_loss - self.entropy * 0.01

            #Get gradients from local network using local losses
            local_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope)
            self.gradients = tf.gradients(self.loss,local_vars)
            self.var_norms = tf.global_norm(local_vars)
            grads, self.grad_norms = tf.clip_by_global_norm(self.gradients, 40.0)

            #Apply local gradients to global network
            global_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, 'global')
            self.apply_grads = trainer.apply_gradients(zip(grads,global_vars))

# Copies one set of variables to another.
# Used to set worker network parameters to those of global network.
#TODO
def update_target_graph(from_scope,to_scope):
    from_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, from_scope)
    to_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, to_scope)

    op_holder = []
    for from_var, to_var in zip(from_vars, to_vars):
        op_holder.append(to_var.assign(from_var))
    return op_holder

# Processes Doom screen image to produce cropped and resized image.
def process_frame(frame):
    s = frame[10:-10, 30:-30]
    s = scipy.misc.imresize(s, [84, 84])
    s = np.reshape(s,[np.prod(s.shape)]) / 255.0
    return s

# Discounting function used to calculate discounted returns.
def discount(x, gamma):
    return scipy.signal.lfilter([1], [1, -gamma], x[::-1], axis=0)[::-1]

#Used to initialize weights for policy and value output layers
def normalized_columns_initializer(std=1.0):
    def _initializer(shape, dtype=None, partition_info=None):
        out = np.random.randn(*shape).astype(np.float32)
        out *= std / np.sqrt(np.square(out).sum(axis=0, keepdims=True))
        return tf.constant(out)
    return _initializer

class Worker():
    def __init__(self, game, name, s_size, a_size, trainer, saver, model_path):
        self.name = "worker_" + str(name)
        self.number = name
        self.model_path = model_path
        self.trainer = trainer
        self.global_episodes = 0
        self.increment = self.global_episodes.assign_add(1)
        self.episode_rewards = []
        self.episode_lengths = []
        self.episode_mean_values = []
        self.summary_writer = tf.summary.FileWriter("train_"+str(self.number))

        self.local_AC = AC_network(s_size, a_size, self.name, trainer)
        self.update_local_ops = update_target_graph('global', self.name)

        game.init()
        self.actions = np.identity(a_size,dtype=bool).tolist()
        self.env = game

    def train(self, rollout, sess, gamma, bootstrap_value):
        rollout = np.array(rollout)
        observations = rollout[:, 0]
        actions = rollout[:, 1]
        rewards = rollout[:, 2]
        next_observations = rollout[:, 3]
        values = rollout[:, 5]

        # Here we take the rewards and values from the rollout, and use them to
        # generate the advantage and discounted returns.
        # The advantage function uses "Generalized Advantage Estimation"
        self.rewards_plus = np.asarray(rewards.tolist() + [bootstrap_value])
        discounted_rewards = discount(self.rewards_plus, gamma)[:-1]
        self.value_plus = np.asarray(values.tolist() + [bootstrap_value])
        advantages = rewards + gamma * self.value_plus[1:] - self.value_plus[:-1]
        advantages = discount(advantages,gamma)

        # Update the global network using gradients from loss
        # Generate network statistics to periodically save
        feed_dict = {self.local_AC.target_v:discounted_rewards, \
            self.local_AC.inputs:np.vstack(observations), \
            self.local_AC.actions:actions, \
            self.local_AC.advantages:advantages, \
            self.local_AC.state_in[0]:self.batch_rnn_state[0], \
            self.local_AC.state_in[1]:self.batch_rnn_state[1]}
        v_l,p_l,e_l,g_n,v_n, self.batch_rnn_state,_ = sess.run([self.local_AC.value_loss, \
            self.local_AC.policy_loss, \
            self.local_AC.entropy, \
            self.local_AC.grad_norms, \
            self.local_AC.var_norms, \
            self.local_AC.state_out, \
            self.local_AC.apply_grads], \
            feed_dict=feed_dict)
        return v_l / len(rollout), p_l / len(rollout), e_l / len(rollout), g_n, v_n

    def work(self, gamma, sess, coord, saver):
        episode_count = sess.run(self.global_episodes)
        total_steps = 0
        print ("Starting worker " + str(self.number))
        with sess.as_default(), sess.graph.as_default():
            while not coord.should_stop():
                sess.run(self.update_local_ops)
                episode_buffer = []
                episode_values = []
                episode_frames = []
                episode_reward = 0
                episode_step_count = 0
                d = False

                self.env.new_episode()
                s = self.env.get_state().screen_buffer
                episode_frames.append(s)
                s = process_frame(s)
                rnn_state = self.local_AC.state_init
                self.batch_rnn_state = rnn_state
                while self.env.is_episode_finished() == False:
                    #Take an action using probabilities from policy network output.
                    a_dist, v, rnn_state = sess.run([self.local_AC.policy, \
                        self.local_AC.value, self.local_AC.state_out], \
                        feed_dict={self.local_AC.inputs:[s], \
                        self.local_AC.state_in[0]:rnn_state[0], \
                        self.local_AC.state_in[1]:rnn_state[1]})
                    a = np.random.choice(a_dist[0], p=a_dist[0])
                    a = np.argmax(a_dist == a)

                    r = self.env.make_action(self.actions[a]) / 100.0
                    d = self.env.is_episode_finished()
                    if d == False:
                        s1 = self.env.get_state().screen_buffer
                        episode_frames.append(s1)
                        s1 = process_frame(s1)
                    else:
                        s1 = s

                    episode_buffer.append([s, a, r, s1, d, v[0, 0]])
                    episode_values.append(v[0, 0])

                    episode_reward += r
                    s = s1
                    total_steps += 1
                    episode_step_count += 1

                    # If the episode hasn't ended, but the experience buffer is full, then we
                    # make an update step using that experience rollout.
                    if len(episode_buffer) == 100 and d != True:
                        # Since we don't know what the true final return is, we "bootstrap" from our current
                        # value estimation.
                        v1 = sess.run(self.local_AC.value, \
                            feed_dict={self.local_AC.inputs:[s], \
                            self.local_AC.state_in[0]:rnn_state[0], \
                            self.local_AC.state_in[1]:rnn_state[1]})[0, 0]
                        v_l, p_l, e_l, g_n, v_n = self.train(episode_buffer, sess, gamma, v1)
                        episode_buffer = []
                        sess.run(self.update_local_ops)
                    if d == True:
                        break

                self.episode_rewards.append(episode_reward)
                self.episode_lengths.append(episode_step_count)
                self.episode_mean_values.append(np.mean(episode_values))

                # Update the network using the episode buffer at the end of the episode.
                if len(episode_buffer) != 0:
                    v_l, p_l, e_l, g_n, v_n = self.train(episode_buffer, sess, gamma, 0.0)


                # Periodically save gifs of episodes, model parameters, and summary statistics.
                if episode_count % 5 == 0 and episode_count != 0:
                    if self.name == 'worker_0' and episode_count % 25 == 0:
                        time_per_step = 0.05
                        images = np.array(episode_frames)
                        make_gif(images, './frames/image'+str(episode_count)+'.gif', \
                            duration=len(images)*time_per_step, true_image=True, salience=False)
                    if episode_count % 250 == 0 and self.name == 'worker_0':
                        saver.save(sess, self.model_path+'/model-'+str(episode_count)+'.cptk')
                        print ("Saved Model")

                    mean_reward = np.mean(self.episode_rewards[-5:])
                    mean_length = np.mean(self.episode_lengths[-5:])
                    mean_value = np.mean(self.episode_mean_values[-5:])
                    summary = tf.Summary()
                    summary.value.add(tag='Perf/Reward', simple_value=float(mean_reward))
                    summary.value.add(tag='Perf/Length', simple_value=float(mean_length))
                    summary.value.add(tag='Perf/Value', simple_value=float(mean_value))
                    summary.value.add(tag='Losses/Value Loss', simple_value=float(v_l))
                    summary.value.add(tag='Losses/Policy Loss', simple_value=float(p_l))
                    summary.value.add(tag='Losses/Entropy', simple_value=float(e_l))
                    summary.value.add(tag='Losses/Grad Norm', simple_value=float(g_n))
                    summary.value.add(tag='Losses/Var Norm', simple_value=float(v_n))
                    self.summary_writer.add_summary(summary, episode_count)

                    self.summary_writer.flush()
                if self.name == 'worker_0':
                    sess.run(self.increment)
                episode_count += 1

def main():
    tf.reset_default_graph()

    if not os.path.exists(model_path):
        os.makedirs(model_path)

    #Create a directory to save episode playback gifs to
    if not os.path.exists('./frames'):
        os.makedirs('./frames')

    with tf.device("/cpu:0"):
        master_network = AC_network(s_size, a_size, 'global', None) # Global network
        num_workers = multiprocessing.cpu_count()
        workers = []
        for i in range(num_workers):
            workers.append(Worker(DoomGame(), i, s_size, a_size, trainer, saver, model_path))

    with tf.Session() as sess:
        coord = tf.train.Coordinator()
        if load_model == True:
            print("Loading Model...")
            cpkt = tf.train.get_checkpoint_state(model_path)
            saver.restore(sess, cpkt.model_checkpoint_path)
        else:
            sess.run(tf.global_variables_initializer())

        worker_threads = []
        for worker in workers:
            worker_work = lambda: worker.work(max_episode_length, gamma, master_network, sess, coord)
            t = threading.Thread(target(worker_work))
            t.start()
            worker_threads.append(t)
        coord.join(worker_threads)

    if env_ver == "v0":
        env = gym.make("cap-v0")
        s_size = 20*20
    elif env_ver == "v1":
        env = gym.make("cap-v1")
        s_size = 100*100
    elif env_ver == "v2":
        env = gym.make("cap-v2")
        s_size = 500*500
    action = env.action_space.sample()  # choose random action
    a_size = len(action)
    done = False
    t = 0

    while not done:
        action = env.action_space.sample()  # choose random action
        # action = [2, 2, 2, 2]
        observation, reward, done, info = env.step(action)  # feedback from environment
        #obs, obs2,  or env
        env.render(mode="env")
        t += 1
        # if not t % 100:
            # print(t, info)
        time.sleep(.25)
        print(reward)
        if t == 100000:
            break

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
