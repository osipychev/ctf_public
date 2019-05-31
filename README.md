# Preparation
We highly recommend using Conda environment to run Capture the Flag simulation.
Please, follow the instructions from Anaconda, Miniconda, etc to install Conda.

Create virtual conda environment from yml file using:
```sh
conda env create -f env.yml
```
or manually install OpenAI GYM, PyGame, Pandas, Numpy using pip if needed.

Activate the virtual environment using:
```sh
source activate ctf
```

Install Cap-Env (or CtF) using python setup script provided. For that, you can run alias.txt file using bash:
```sh
cat alias.txt | bash
```
or do it manually.

Look at cap_test.py file for examples and run it to test if the environment works. Feel free to use the provided policies in Policy folder to develop your own one.

## Package Install

For installation:

``` sh
pip install git+https://github.com/raide-project/ctf_public
```

For update:

``` sh
pip install -U git+https://github.com/raide-project/ctf_public
```

## Policy Rule

- The environment takes input as a tuple.
    - The number of element in tuple must match the total number of blue agent. (UAV+UGB)
    - The action must be in range between 0 and 4.
- If UAV is included, the UAV's action comes __in front__ of UGV's action.
    - ex) To make UAV to hover (fix): action = [0, 0] + [UGV's action]

## Debugging Utilities

- Playing in customized board: 

By passing the directory of custom board in text file, environment will use provided board setting to override board terrain and number of agents.

cap_test.py
```py
...
observation = env.reset(
    policy_blue=policy.random.PolicyGen(env.get_map, env.get_team_blue),
    policy_red=policy.random.PolicyGen(env.get_map, env.get_team_red),
    custom_board='test_maps/board2.txt'
    )
...
```

test_map/board2.txt
```py
0 0 2 4 1 4 1 1 1
2 2 8 8 4 1 1 1 1
0 0 8 8 1 1 1 1 1
6 0 0 1 1 7 0 0 0
0 0 0 1 8 8 0 0 0
0 0 2 4 8 8 0 0 0
1 1 1 0 0 0 1 1 1
1 1 1 0 0 0 1 1 1
1 1 1 0 0 0 1 1 1
```
* board elements are separated by space.


- Custom Initialization

The environment is mostly fixed with default configuration numbers, but some numbers are possible to be altered by passing a configuration file.

cap_test.py
``` py
...
observation = env.reset(
    map_size=20,
    policy_blue=policy.random.PolicyGen(env.get_map, env.get_team_blue),
    policy_red=policy.random.PolicyGen(env.get_map, env.get_team_red),
    config_path='config.ini'
    )
...
```

config.ini
``` py
[elements]
NUM_BLUE=4
NUM_RED=4
NUM_UAV=2
NUM_GRAY=0

[settings]
STOCH_ATTACK = True
STOCH_ZONES = True
RL_SUGGESTIONS = False
STOCH_TRANSITIONS = False
RED_PARTIAL = False
BLUE_PARTIAL = False
```

## Policy Evaluation

cap_eval.py : Testing script analyzes the total rate of win, rate of win by capturing flag, rate of win by killing the other team and plots histogram of the mean score of a team in all episodes. It also prints the mean score, standard deviation of the mean score, total time for all episodes and for one episode and average steps taken per episodes.

Example)
``` bash
python cap_eval.py --episode 3000 --blue_policy roomba
```

### Valid Arguments

- episode: number of iterations to analyze (default: 1000)
- blue_policy: policy to be implmented for blue team (default: random)
- red_policy: policy to be implmented for blue team (default: random)
- num_blue: number of blue ugv agents (default: 4)
- num_red: number of red ugv agents (default: 4)
- num_uav: number of uav agents (default: 0)
- map_size: size of map (default: 20)
- time_step: maximum number of steps per iteration to be completed by the teams (default: 150)

```py
> python cap_eval.py --episode 50 --blue_policy roomba

Episodes Progress Bar

100%|██████████████████████████████████████████████████████████████████████████████████| 50/50 [00:03<00:00, 14.66it/s]
-------------------------------------------- Statistics --------------------------------------
win # overall in 50 episodes: {'BLUE': 31, 'NEITHER': 1, 'RED': 18}
win # in capturing flag    : {'BLUE': 4, 'NEITHER': 15, 'RED': 31}
win # in killing other team: {'BLUE': 14, 'NEITHER': 36}
time per episode: 0.06638088703155517 s
total time: 3.5574886798858643 s
mean steps: 3318.1
