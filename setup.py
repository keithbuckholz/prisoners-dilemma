import setuptools

setuptools.setup(
     name="prisoners_dilemma",
     version="0.1",
     author="Keith Buckholz",
     author_email="keith.buckholz@yale.edu",
     description="Prisoner's Dilemma Simulation",
     packages=["prisoners_dilemma", "prisoners_dilemma/bots", "prisoners_dilemma/game"],
     python_requires=">=3",
     install_requires=["numpy", "matplotlib"]
)