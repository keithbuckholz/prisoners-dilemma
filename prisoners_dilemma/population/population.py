import os
import sys
from prisoners_dilemma.tournament import dilemma_tournament, define_players
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import imageio

class population_mode(dilemma_tournament):
	"""
	This class places players on a map with certain decision making algorithms. 
	Each round tests each player against only it's neighbors some number of 
	times. Then, the worst performers of the population randomly change 
	strategies/decision-making-algorithms. After some number of rounds or when
	a predetermined amount of the population is using the same algorithm, the 
	simulation ends. After the simulation ends, the results are made into 
	images and those images are turned into a gif all in a folder named 
	dilemma-fields.

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
		mean of 50 and standard deviation of 2
	evolutions: int, optional
		Maximum number of field evolutions before simulation stops. In case of
		oscilation, this will prevent the sim from continuing indefinitely.
		default: 100
	field_size: tuple of 2 ints, optional
		This determines the size of the field. default: (10, 10)
	rng_seed: int, optional
		rng seed can be given for replicability. Note: this seed in not passed
		to player algorithms. Player algorithm behavior may prevent perfect
		replication. default: None
	quantile: float between 0 and 1, optional
		How much of the map should be replaced each round. 0 would replace
		nobody, 0.01 would replace the lowest 1%, and 1 would replace
		everybody. default: 0.2
	win_condition: float between 0 and 1, optional
		How much of the map must be taken before declaring a victor. 
		default: 0.5
	"""

	def __init__(self, players=None, n_rounds=None, evolutions=100,
	             field_size=(10, 10), rng_seed=None, quantile=0.2,
				 win_condition=0.5):
		super().__init__(players, n_rounds, rng_seed)

		# Initialize temp field and score arrays
		self.field = np.zeros(field_size)
		self.score_array = np.zeros(field_size)

		# Define Players
		enumeration = enumerate(define_players(players))
		self.players = {number: player for number, player in enumeration}

		# Set end conditions/flags & define rng seed
		self.evolutions = evolutions
		self.convergence = False
		self.win_condition = win_condition

		# Define variables for later use
		self.rng = np.random.default_rng(rng_seed)
		self.quantile = 0.2

		# Initialize historical field and score cubes
		cube_shape = (0,) + field_size
		self.field_cube = np.empty(cube_shape)
		self.score_cube = np.empty(cube_shape)


	def spawn(self):
		"""
		This method intially populated the field. Every player/point is
		assigned a random algorithm such that the field is filled and 
		randomized to start.
		"""
		for ii in range(self.field.shape[0]):
			for nn in range(self.field.shape[1]):
				self.field[ii,nn] = self.rng.choice(list(self.players.keys()))
		return self

	def round(self):
		"""
		Runs a single round. Iterates through every player on the field from 
		right to left, top to bottom. Tests every player-algorithm against all
		neighbors below and to their immediate right. This ensure all player-
		algorithms are only tested against each neighbor once. After finishing
		a point's interation, that point's score is normalized to the number of
		neighbors it has. This prevents the edge and corner positions from
		unfair disadvantage.
		"""
		for ii in range(self.field.shape[0]):
			for nn in range(self.field.shape[1]):

				# Define this bot and identify neighbors
				this_bot = self.field[ii, nn]
				neighbor_indices = [
					(ii - 1, nn),  # Top neighbor
					(ii + 1, nn),  # Bottom neighbor
					(ii, nn - 1),  # Left neighbor
					(ii, nn + 1),  # Right neighbor
					(ii - 1, nn - 1), # Top-left neighbor
					(ii + 1, nn - 1), # Bottom-left neighbor
					(ii + 1, nn + 1), # Bottom-right neighbor
					(ii - 1, nn + 1) # Top-right neighbor
				]

				# Filter out edge cases
				valid_neighbor_indices = [(jj, kk) for jj, kk in neighbor_indices 
										  if 0 <= jj < self.field.shape[0] and 
										  0 <= kk < self.field.shape[1]]

				# Select only Lower and Right Neighbors
				relevant_neighbor_indicies = [(jj, kk) for jj, kk in valid_neighbor_indices
											  if (jj > ii or kk > nn) and not (jj > ii and kk < nn)]

				# Gather list of neighbor functions with indicies
				neighbors = [(self.field[index], index) for index in valid_neighbor_indices]
				for neighbor in neighbors:
					self.matchup(self.players[this_bot], 
					             self.players[neighbor[0]], 
								 (ii, nn), 
								 neighbor[1])
				
				self.score_array[ii, nn] = (self.score_array[ii, nn] /
										   len(valid_neighbor_indices))
		
		return self

	def matchup(self, bot_1, bot_2, bot_1_loc, bot_2_loc):
		"""
		This method runs some number of rounds of the prisoners dilemma by 
		gathering each players deicision to cooperate of defect then calling 
		the award_points method (inherited from the tournament class) n times.
		This method records all match information to the score_array instance 
		attribute.

		Parameters
		----------
		bot_1: function
			Player algorithm.
		bot_2: function
			Player algorithm.
		bot_1_loc: tuple
			tuple indexing bot_1's position on the field
		bot_2_loc: tuple
			tuple indexing bot_2's position on the field
		"""
		nn = self.n_rounds
		if not nn: # Random number of rounds if not user defined
			nn = round(self.rng.normal(50, 2)) # Normal ditribution mean=50, one_sigma=2
		bot_1_history = []
		bot_2_history = []

		# Run game nn number of times
		for ii in range(nn):

			# Collect bot decisions
			decision_1 = bot_1(bot_2_history)
			decision_2 = bot_2(bot_1_history)

			# Run dilemma, store score_tuple
			score_tuple = self.award_points(decision_1, decision_2)

			# Unpack score_tuple and update scores
			self.score_array[bot_1_loc] += score_tuple[0]
			self.score_array[bot_2_loc] += score_tuple[1]

			# Format each rounds results
			round_info = [[bot_1.__name__, decision_1, score_tuple[0]],
						[bot_2.__name__, decision_2, score_tuple[1]]]

			# Update this matches history
			bot_1_history.append(round_info[0])
			bot_2_history.append(round_info[1])

		return self
	
	def respawn(self):
		"""
		This method changes those lowest scoring players on the field to a
		random new algorithm. It sets a cutoff score at the given quantile.
		Then replaces all players scoring below that mark. All changed players
		will change to the same new algorithm.

		While changing players' algorithms, this method stores the current
		score and field state in the score cube and field cube respectivelly.
		Lastly, this method clears the score_array.

		"""

		# Store current field state
		self.field_cube = np.concatenate((self.field_cube, 
						np.expand_dims(self.field, axis=0)), 
						axis=0) # Add array to cube

		# Determine indicies to respawn
		cutoff_score = int(np.quantile(self.score_array[1:-1, 1:-1], self.quantile))

		# Respawn lowest scorers
		boolray = self.score_array <= cutoff_score
		self.field[boolray] = self.rng.choice(list(self.players.keys()))

		# Store score state
		self.score_cube = np.concatenate((self.score_cube, 
										  np.expand_dims(self.score_array, axis=0)), 
										  axis=0) # Add array to cube
		self.score_array = np.zeros(self.field.shape) # Empty array
		return self

	def check_convergence(self):
		"""
		This method checks if the win_condition had been met by any algorithm.
		If it has, this method set the convergence flag to True.
		"""

		if len(np.unique(self.field)) == 2:
			self.convergence = True

		dominator = np.quantile(self.field, 1)

		if dominator == np.quantile(self.field, self.win_condition):
			print(self.players[dominator].__name__, "has met the win condition.")
			self.convergence = True

		return self

	def generate_images(self):
		"""
		At the end of the simulation, this method iterates throught the field
		cube and turns every field state into a unique image titled with which
		step in the evolution is depicted and a colorbar to indicated which
		algorithms are being shown. Images are saved in a folder named
		dilemma-fields, overwriting and images previously saved in the folder.
		"""

		# Define custom colormap
		possible_colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'orange', 'purple', 'pink', 'brown']
		custom_colors = [possible_colors[ii] for ii in self.players.keys()]
		cmap_custom = mcolors.ListedColormap(custom_colors)

		# Loop through the cube
		for ii, state in enumerate(self.field_cube):

			# Normalize state value to make colors predictable
			norm_state = state / np.max(state)

			# Show and title image
			plt.imshow(norm_state, cmap=cmap_custom)
			plt.title(f"Evolution step:{ii:02d}")

			# Create colorbar key
			unique_values = np.unique(state)
			cbar = plt.colorbar()
			cbar.set_ticks([key/len(self.players) for key in self.players.keys()])
			cbar.set_ticklabels([function.__name__ for function in self.players.values()]) 

			# Create a folder for the images, prepare the filename
			output_dir = "./dilemma-fields"
			os.makedirs(output_dir, exist_ok=True)
			
			image_path = f"{output_dir}/evo{ii:02d}.png"

			output_dir = "./dilemma-fields"
			os.makedirs(output_dir, exist_ok=True)

			# Save figure, close plot to avoid mem leaks
			plt.savefig(image_path)
			plt.close()
		return self

	def generate_gif(self):
		"""
		Calls the generate_images method to produce .png images from every
		field state. Then, this method turns those .png images into a gif to
		make trends and emergent behaviors more clear. gif is save in a folder
		name dilemma-fields with the images. Overwrites any previously saved
		gif in the folder. Filename: dilemma-field-evolution.gif
		"""

		self.generate_images()

		images = []
		for filename in sorted(os.listdir("./dilemma-fields")):
			if filename.endswith('.png'):
				file_path = os.path.join("./dilemma-fields", filename)
				images.append(imageio.imread(file_path))
		imageio.mimsave("dilemma-fields/dilemma-field-evolution.gif", images, duration=0.75)  # Adjust duration as needed

		return self

	def run(self, return_field_cube=False, return_score_cube=False):
		"""
		This method runs the population simulation to it's conclusion. This
		conclustion is either after so many evolutions or after a convergence
		occurs and a winner is declared. This method does not generate images
		or gifs on its own. That method must be called afterwards.

		Parameters
		----------
		return_field_cube: bool, optional
			Returns cube containing every field state instead of self. If 
			return_score_cube is also True, both are returned. Note: does not 
			return self and other methods cannot be chained. 
			default: False
		return_score_cube: bool, optional
			Returns cube containing all score arrays instead of self. If 
			return_field_cube is also True, both are returned. Note: does not 
			return self and other methods cannot be chained. 
			default: False 
		"""
		self.spawn()
		while self.evolutions > 0 and not self.convergence:
			self.round()
			self.check_convergence()
			self.respawn()
			self.evolutions -= 1

		if return_field_cube and return_score_cube:
			return self.field_cube, self.score_cube
		if return_field_cube:
			return self.field_cube
		if return_score_cube:
			return self.score_cube
		return self

def population():
	"""
	Intended for command line usage. Parses sys.argv list into kwargs. Then,
	runs full population simulation and generates images and gif. For possible
	kwargs, see population_mode class and its run() method.
	"""
	# Possible arguments
	possible_args = ["players", "n_rounds", "evolutions", "field_size",
					 "rng_seed", "quantile", "win_condition"]
	int_args = ["n_rounds", "evolutions", "rng_seed"]
	float_args = ["quantile", "win_condition"]
	pop_args = ["show_scores", "return_scores", "return_all_results"]
	given_args = sys.argv[1:]

	kwargs = {}
	pwargs = {}

	# Store arguments as kwargs
	for argv in given_args:
		try:
			key, value = argv.split('=')
		except ValueError as e:
			message = f"{argv} is not valid. Arguments must be 'argument=value' with no whitespace."
			raise e from ValueError(message)

		# Handle population kwargs
		if key in pop_args:
			if value == "False":
				value = False
			twargs[key] = bool(value)
			continue

		# Check that kwargs are valid
		assert key in possible_args, f"{key} is not a valid kwarg. kwargs must be one of:{possible_args}"

		try:

			# Parse all integer arguments
			if key in int_args:
				kwargs[key] = int(value)

			# Float Arguments
			if key in float_args:
				kwargs[key] = float(value)

			# Parse field size
			if key == "field_size":
				values = value.strip("()").split(",")
				tuple_value = tuple(int(v) for v in values)
				kwargs[key] = tuple_value


			# Parse player script
			if key == "players":
				if value[-3:].lower() == ".py":
					value = value[:-3]
				kwargs[key] = value
			
		except ValueError as e:
			# Message written here for formatting and terminal readability
			message = (f"Invalid value for {key}={value}. "
						"this kwarg must be an integers.")
			raise e from ValueError(message)

	if pwargs:
		population_mode(**kwargs).run(**pwargs)
	else:
		population_mode(**kwargs).run().generate_gif()
	return 0