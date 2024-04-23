"""
Inspiration: https://www.youtube.com/watch?v=mScpHTIi-kM
This has already been done: https://ncase.me/trust/

This script runs a prisoner's dilemma simulation with mutliple participants 
over an unknown number of rounds.

All player algorithms must be functions stored in a file name bots.py, which will be imported to run the simulation.
"""

import sys
import importlib
import numpy as np
from inspect import isfunction
from prisoners_dilemma import bots

def import_user_bots(filename):
	try:
		# Try to import the package
		module = importlib.import_module(filename)
		return module
	
	except ImportError:
		print(f"Error: Unable to import '{filename}'.")
		return 1

def define_players(players):
	"""
	Defines list_of_players using built-in bots, plus any algorithms provided by the user.
	"""
	# Import built-ins
	list_of_players = [getattr(bots, item) for item in dir(bots) 
    	               if isfunction(getattr(bots, item))]
	
	# If defined, import player algorithms
	if not players==None:
		user_bots = [getattr(players, item) for item in dir(players) 
    	               if isfunction(getattr(players, item))]
		list_of_players.extend(user_bots)

	# Return full list of player algorithms
	return list_of_players

class dilemma_tournament():
	"""
	The Prisoner's Dilemma is a game between two players. The players may 
	choose to "cooperate" or "defect." Both players cooperations grants both
	players 2 points. Both players defection grants no points. If one player
	defect while the other cooperates, the defector gets 3 points and the 
	cooperator gets -1 points.

	This class runs a tournament of prisoner's dilemmas. It calls the 
	Define_players function to define the player algorithms. Then tests
	each algorithm against every other algorithm and prints the final results.
	"""
	
	def __init__(self, players=None, n_rounds=None):
		# Player Algorithms
		self.players = define_players(players)
		# Number of rounds in each matchup
		self.n_rounds = n_rounds
		self.rng = np.random.default_rng()
		# Instance attirbutes for tracking wins/losses
		self.all_results = []
		self.readable_results = []
		self.final_scores = {player.__name__: 0 for player in self.players}


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
		if decision_1: # Decision are boolean values where True==Cooperate
			if not decision_2:
				return (-1, 3) # Cooperate/Defect
			elif decision_2:
				return (2, 2) # Cooperate/Cooperate
		
		elif not decision_1:
			if not decision_2:
				return (0, 0) # Defect/Defect
			elif decision_2:
				return (3, -1) # Defect/Cooperate

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
		show_scores: bool, False
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
	

	

# Code allowing command line usage is below this comment
def tournament():
	"""
	Runs tournament with built-in bots in the command line
	"""

	module=None

	# If player define bot file to include
	if len(sys.argv) > 1:
		# Parse user input
		players = sys.argv[1]
		if players[-3:].lower == ".py":
			players = players[:-3]

		# Import user algorithms, and set variable to track module
		module = import_user_bots(players)

	# Run tournament. If user did not define file, module==None
	dilemma_tournament(players=module).tournament()
	return 0


def credits():
	print("""
	Inspiration: https://www.youtube.com/watch?v=mScpHTIi-kM
	This has already been done: https://ncase.me/trust/
	""")
	return 0