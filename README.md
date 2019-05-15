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
