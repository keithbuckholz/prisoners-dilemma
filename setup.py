import setuptools

setuptools.setup(
     name="prisoners-dilemma",
     version="1.0",
     author="Keith Buckholz",
     author_email="keith.buckholz@yale.edu",
     description="Prisoner's Dilemma Simulation",
     packages=["prisoners_dilemma", "prisoners_dilemma/bots", "prisoners_dilemma/tournament", "prisoners_dilemma/population"],
     python_requires=">=3",
     install_requires=["numpy", "matplotlib", "imageio"],
     entry_points={
          "console_scripts" : [
               "dilemma-tournament = prisoners_dilemma.tournament:tournament",
               "dilemma-population = prisoners_dilemma.population:population",
               "dilemma-credits = prisoners_dilemma.tournament:credits"
          ]
     }
)