from setuptools import setup

setup(name="gym_cap",
      version="0.2",
      author="Me",
      license="MIT",
      packages=["gym_cap", "gym_cap.envs"],
      package_data = {
          "gym_cap.envs": ["ctf_samples/*.npy"]
      },
      include_package_data=True,
      zip_safe=False,
      install_requires = ["gym", "pygame", "numpy"]
)
