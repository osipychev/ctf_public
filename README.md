## Preparation
We highly recommend to use Conda environment to run Capture the Flag simulation.
Please, follow the instructions from Anaconda, Miniconda, etc to install Conda.

Create virtual conda environment from yml file using:
conda env create -f env.yml
or manually install OpenAI GYM, PyGame, Pandas, Numpy using pip if needed

Install Cap-Env (or CtF) using python setup script provided. For that, you can run alias.txt file using bash:
cat alias.txt | bash
or do it manually

Look at cap_test.py file for examples and run it to test if the environment works.
Feel free to use the provided policies in Policy folder to develop your own one.
