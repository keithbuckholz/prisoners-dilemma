import sys
import os
import importlib
import numpy as np
from inspect import isfunction
from prisoners_dilemma import bots

def import_user_bots(filepath):
	"""
	This function imports a users file full of player algorithms.

	Parameters
	----------
	filename: str
		Name of the python script to be imported, not including .py extension.
	"""
	# If user attempting to skip import, do not import. Return 0
	if filepath==None or filepath=="None":
		return 0

	try:
		# Try to import the package
		path, file = os.path.split(filepath)
		sys.path.append(path)
		if file[-3:].lower() == '.py':
			file = file[:-3]
		module = importlib.import_module(file)
		return module
	
	except ImportError as e:
		message = f"Error: Unable to import '{filename}'."
		raise e from ImportError(message)

def define_players(players):
	"""
	Defines list_of_players using built-in bots, plus any algorithms provided
	by the user.

	Parameters
	----------
	players: str
		Name of python script defining player functions, not including .py
		extesion.
	"""
	# Import built-ins
	list_of_players = [getattr(bots, item) for item in dir(bots) 
    	               if isfunction(getattr(bots, item))]
	
	# If defined, import player algorithms
	if not players==None:
		players = import_user_bots(players)

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

	This class runs a series of prisoner's dilemmas. It defines all player 
	algorithms using built-in bots from the prisoners-dilemma/bots package
	and using functions in a user-defined python script. It contains methods
	used to award points for decisions, test two player algorithms against each
	other and test all player algorithms against all other player algorithms.
	
	Parameters
	----------
	players: str, optional
		Name of .py script containing algorithms the user wants included. Note:
		algorithms must take in 1 argument that is nested lists containing 
		opponent information. Player algorithms must return a bool for which 
		True indicates Cooperation.
	n_rounds: int, optional
		Number of rounds played between each player algorithm. By default, the
		number of rounds played are randomly selected from a gaussian with a
		mean of 200 and standard deviation of 10
	rng_seed: int, optional
		rng seed can be given for replicability. Note: this seed in not passed
		to player algorithms. Player algorithm behavior may prevent perfect
		replication. default: None
	"""
	
	def __init__(self, players=None, n_rounds=None, rng_seed=None):
		# Player Algorithms
		self.players = define_players(players)

		# Number of rounds in each matchup
		self.n_rounds = n_rounds
		self.rng = np.random.default_rng(rng_seed)

		# Instance attirbutes for tracking wins/losses
		self.all_results = []
		self.readable_results = []
		self.final_scores = {player.__name__: 0 for player in self.players}


	def award_points(self, decision_1, decision_2):
		"""
		Awards points for decisions on a single prisoner's dilemma. Decisions
		will be evaluated as booleans where True indicates Cooperation.

		Parameters
		----------
		decision_1: bool
			The first player's decisions.
		decision_2: bool
			The second player's decisions.
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

		raise ValueError("Players must return Boolean where True==Cooperate")


	def matchup(self, bot_1, bot_2):
		"""
		This method runs some number of rounds of the prisoners dilemma by 
		calling the award_points method n times. This method records all match 
		information to all_results instance attribute, and awards points to the
		final_score instance attribute.

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
			nn = round(self.rng.normal(200, 10)) # Normal ditribution mean=200,
			                                     # one_sigma=10
		bot_1_history = []
		bot_2_history = []

		# Run game nn times
		for ii in range(nn):

			# Collect bot decisions
			decision_1 = bot_1(bot_2_history)
			decision_2 = bot_2(bot_1_history)

			# Run dilemma once, store score_tuple
			score_tuple = self.award_points(decision_1, decision_2)

			# Unpack score_tuple and update final scores
			self.final_scores[bot_1.__name__] += score_tuple[0]
			self.final_scores[bot_2.__name__] += score_tuple[1]

			# Format each rounds results
			round_info = [[bot_1.__name__, decision_1, score_tuple[0]],
						[bot_2.__name__, decision_2, score_tuple[1]]]

			# Update this matches history
			bot_1_history.append(round_info[0])
			bot_2_history.append(round_info[1])

		# Update object history with this rounds information
		self.all_results.append([bot_1_history, bot_2_history])

		return self

	def tournament(self, show_scores=True, return_all_results=False, 
				   return_scores=False):
		"""
		This method tests every player algorithm against each other. Each
		player algorithm will play one "match" with each other player algorithm
		once. A "match" is defined as some number of consecutive rounds. At the
		end, the final score as well as a few benchmarks as printed.

		Parameters
		----------
		show_scores: bool
			Prints the final score after tournament is run. default: True
		return_all_results: bool
			Returns results of every single dilemma instead of self. Note: if 
			True, does not return self and other methods cannot be chained. 
			default: False
		return_scores: bool
			Returns final scores instead of self. Note: if True, does not 
			return self and other methods cannot be chained. default: False
		"""

		# Loops through bots, testing against all other bots
		for ii, bot_1 in enumerate(self.players):
			for bot_2 in self.players[ii+1:]:
				self.all_results.append(self.matchup(bot_1, bot_2))

		# Calculate Benchmark scores
		if not self.n_rounds:
			n_rounds = 200
		else:
			n_rounds = self.n_rounds
		
		max_points = n_rounds * (len(self.players) - 1) * 3
		min_points = n_rounds * (len(self.players) - 1) * -1
		perf_coop = n_rounds * (len(self.players) - 1) * 2

		benchmarks = ("Benchmarks - Exact if n_rounds is defined\n"
		"------------------------------ \n"
		f"Approximate Maximum Points: {max_points} \n"
		f"Approximate Minimum Points: {min_points} \n"
		f"Perfect Cooperation: {perf_coop} \n")

		# Show scores and return
		if show_scores:
			print("\n" + benchmarks)
			for bot, score in self.final_scores.items():
				print(f"{bot}: {score}")
		if return_all_results:
			return self.all_results
		if return_scores:
			return self.final_scores
		return self
	

	

# Code allowing command line usage is below this comment
def tournament():
	"""
	Intended for command line usage. Parses sys.argv list into kwargs. Then,
	runs full tournament simulation and print results and benchmarks in
	command line. For possible kwargs, see dilemma_tournament class and its 
	tournament() method.
	"""
	# Possible arguments
	possible_args = ["players", "n_rounds", "rng_seed"]
	tourni_args = ["show_scores", "return_scores", "return_all_results"]
	given_args = sys.argv[1:]

	kwargs = {}
	twargs = {}

	# Store arguments as kwargs
	for argv in given_args:
		try:
			key, value = argv.split('=')
		except ValueError as e:
			message = (f"{argv} is not valid. Arguments must be "
			            "'argument=value' with no whitespace.")
			raise e from ValueError(message)

		# Handle Tournament kwargs
		if key in tourni_args:
			if value == "False":
				value = False
			twargs[key] = bool(value)
			continue

		# Check that kwargs are valid
		assert key in possible_args, (f"{key} is not a valid kwarg. kwargs must "
		                               "be one of:{possible_args}")

		try:

			# All arguments other that players are integers
			if key != "players":
				kwargs[key] = int(value)

			# Parse player script
			if key == "players":
				kwargs[key] = value
			
		except ValueError as e:
			message = (f"Invalid value for {key}={value}. "
						"this kwarg must be an integers.")
			raise e from ValueError(message)

	dilemma_tournament(**kwargs).tournament(**twargs)
	return 0


def credits():
	"""
	This method is accessible from command line and provides credit to the 
	inspiration for this python package.
	"""
	print("""
	Inspiration: https://www.youtube.com/watch?v=mScpHTIi-kM
	This has already been done: https://ncase.me/trust/
	""")
	return 0