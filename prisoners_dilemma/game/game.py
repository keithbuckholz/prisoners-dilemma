"""
Inspiration: https://www.youtube.com/watch?v=mScpHTIi-kM
This has already been done: https://ncase.me/trust/

This script runs a prisoner's dilemma simulation with mutliple participants 
over an unknown number of rounds.

All player algorithms must be functions stored in a file name bots.py, which will be imported to run the simulation.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from inspect import isfunction
from prisoners_dilemma import bots

# Extract all callable functions from "bot" module
list_of_players = []

def define_players():
	list_of_players = [getattr(bots, item) for item in dir(bots) 
    	               if isfunction(getattr(bots, item))]
	return 0

class prisoners_dilemma():
	
	def __init__(self, players, n_rounds=None):
		# Player Algorithms
		self.players = [bot for bot in players]
		# Number of rounds in each matchup
		self.n_rounds = n_rounds
		self.rng = np.random.default_rng()
		# Instance attirbutes for tracking wins/losses
		self.all_results = []
		self.readable_results = []
		self.final_scores = {player.__name__: 0 for player in players}


	def award_points(self, decision_1, decision_2):
		"""
		Awards points for decisions on a single prisoner's dilemma. Decisions
		will be evaluated as booleans where True is Cooperation.

		Parameters
		----------
		decision_1: bool
			The player's decisions. Will be evaluated as booleans where True is Cooperation.
		decision_2: bool
			The player's decisions. Will be evaluated as booleans where True is Cooperation.
		"""

		# Check decisions and award points
		if decision_1: # Decision are boolean values where true is cooperation.
			if not decision_2:
				return (-1, 3)
			elif decision_2:
				return (2, 2)
		
		elif not decision_1:
			if not decision_2:
				return (0, 0)
			elif decision_2:
				return (3, -1)

		raise ValueError


	def matchup(self, bot_1, bot_2):
		"""
		This method runs n rounds of the prisoners dilemma by calling the award_points method n times.
		This method records all match information to all_results instance attribute, and awards points
		to the final_score instance attribute.

		Parameters
		----------
		bot_1: function
			Player algorithm.
		bot_2: function
			Player algorithm.
		"""
    
		# Initialize Matchup
		nn = self.n_rounds
		if not nn: # Random number of rounds if not user defined
			nn = round(self.rng.normal(200, 10)) # Normal ditribution mean=200, one_sigma=10
		bot_1_history = []
		bot_2_history = []

		# Run game repeatedly
		for ii in range(nn):

			# Collect bot decisions
			decision_1 = bot_1(bot_2_history)
			decision_2 = bot_2(bot_1_history)

			# Run dilemma, store score_tuple
			score_tuple = self.award_points(decision_1, decision_2)

			# Unpack score_tuple and update scores
			self.final_scores[bot_1.__name__] += score_tuple[0]
			self.final_scores[bot_2.__name__] += score_tuple[1]

			# Format each rounds results
			round_info = [[bot_1.__name__, decision_1, score_tuple[0]],
						[bot_2.__name__, decision_2, score_tuple[1]]]

			# Update this matches history
			bot_1_history.append(round_info[0])
			bot_2_history.append(round_info[1])

		# Update object history with this rounds information
		self.all_results.append([bot_1_history, bot_2_history]) # Record all matchup info

		return self

	def tournament(self, show_scores=True, show_match_info=False):
		"""
		This method runs a tournament, testing all players against all other players.

		Parameters
		----------
		show_scores: bool
			Prints the final scores
		show_match_info: bool
			Prints all matches' information.
		"""

		# Loops through bots
		for ii, bot_1 in enumerate(self.players):
			for bot_2 in self.players[ii+1:]:
				self.all_results.append(self.matchup(bot_1, bot_2))

		if show_scores:
			for bot, score in self.final_scores.items():
				print(f"{bot}: {score}")
		if show_match_info:
			print(self.all_results)
		return self
	

class population_mode(prisoners_dilemma):
	"""
	This class places player algorithms on a map. Each round tests each 
	algorithm against only it's neighbors N times. Then, the worst performing
	fifth of the population randomly changes strategies. After some number of
	rounds or when the top four-fifths of the population is the same algorithm,
	the simulation ends.
	"""

	def __init___(self, players, n_rounds=None, inital_pop=10, field_size=(100, 100)):
		super().__init__(players, n_rounds)
		self.field = np.zeros(field_size)

	

# Code allowing Command-line usage is below this comment
if len(sys.argv) > 1:
	if sys.argv[1] == "tournament":
		prisoners_dilemma(list_of_players).tournament()

# if len(sys.argv) > 1:
# 	if sys.argv[1] == "population":
# 		population_mode(list_of_players).gambit()