import setuptools

setuptools.setup(
     name="prisoners-dilemma",
     version="0.1",
     author="Keith Buckholz",
     author_email="keith.buckholz@yale.edu",
     description="Prisoner's Dilemma Simulation",
     packages=["prisoners_dilemma", "prisoners_dilemma/bots", "prisoners_dilemma/game"],
     python_requires=">=3",
     install_requires=["numpy", "matplotlib"],
     entry_points={
          "console_scripts" : [
               "dilemma-tournament = prisoners_dilemma.game:tournament",
               "dilemma-population = prisoners_dilemma.game:population",
               "dilemma-credits = prisoners_dilemma.game:credits"
          ]
     }
)