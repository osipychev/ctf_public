import pickle
import numpy as np


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))  # sigmoid "squashing" function to interval [0,1]


def prepro(I):
    """ prepro frame into (20x20) 1D float vector """
    return I.astype(np.float).ravel()


def policy_forward(x, model):
    h = np.dot(model['W1'], x)
    h[h < 0] = 0  # ReLU nonlinearity
    logp = np.dot(model['W2'], h)
    p = sigmoid(logp)
    return p  # return probability of taking action 2, and hidden state


def predict_move(env, model):
    x = prepro(env)
    aprob = policy_forward(x, model)
    aprob = aprob / np.sum(aprob)
    # action = np.random.choice(5, p=aprob)
    return aprob


def load_model(file_name):
    model = pickle.load(open('gym_cap/gym_cap/envs/Models/' + file_name, 'rb'))
    return model
