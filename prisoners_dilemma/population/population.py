import sys
from prisoners_dilemma.tournament import dilemma_tournament, define_players
import numpy as np
import matplotlib.pyplot as plt
import imageio

class population_mode(dilemma_tournament):
	"""
	This class places player algorithms on a map. Each round tests each 
	algorithm against only it's neighbors N times. Then, the worst performing
	fifth of the population randomly changes strategies. After some number of
	rounds or when the top four-fifths of the population is the same algorithm,
	the simulation ends.
	"""

	def __init__(self, players=None, n_rounds=None, evolutions=None, field_size=(20, 20)):
		super().__init__(players, n_rounds)
		self.field = np.zeros(field_size)
		enumeration = enumerate(define_players(players))
		self.players = {number: player for number, player in enumeration}
		# Temporary evolutions value
		self.evolutions = 1
		self.score_array = np.zeros(field_size)

		cube_shape = field_size + (2,)
		self.field_cube = np.empty(cube_shape)
		self.score_cube = np.empty(cube_shape)

	def spawn(self):
		for ii in range(self.field.shape[0]):
			for nn in range(self.field.shape[1]):
				self.field[ii,nn] = self.rng.choice(list(self.players.keys()))
		return self

	def round(self):
		"""
		Runs a single round 
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
		nn = self.n_rounds
		if not nn: # Random number of rounds if not user defined
			nn = round(self.rng.normal(50, 2)) # Normal ditribution mean=200, one_sigma=10
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
		# Store current field state
		np.concatenate((self.field_cube, 
						np.expand_dims(self.field, axis=2)), 
						axis=2) # Add array to cube

		# Determine indicies to respawn
		replace_n = (self.field.shape[0] * self.field.shape[1])//20
		flat_indices = np.argsort(self.field.flatten())
		true_indicies = np.unravel_index(flat_indices[:replace_n], self.field.shape)

		# Respawn those indicies
		for ii in true_indicies[0]:
			for nn in true_indicies[1]:
				self.field[ii,nn] = self.rng.choice(list(self.players.keys()))

		self.score_cube = np.concatenate((self.score_cube, 
										  np.expand_dims(self.score_array, axis=2)), 
										  axis=2) # Add array to cube
		self.score_array = np.zeros(self.field.shape) # Empty array
		return self

	def generate_images(self):
		"""
		This method displays the current population field. 
	
		No Parameters.
		"""
		# Loop through the cube
		for ii, state in enumerate(self.field_cube[2]):

			# Open image,create folder for images, prepare filename
			plt.imshow(state)
			output_dir = "./dilemma-fields"
			os.makedirs(output_dir, exist_ok=True)
			image_path = f"{output_dir}/evo{ii}.png"

			output_dir = "./dilemma-fields"
			os.makedirs(output_dir, exist_ok=True)

			# Save figure, close plot to avoid mem leaks
			plt.savefig(image_path)
			plt.close()
		return self

	def generate_gif(self):

		self.generate_images()

		images = []
		for filename in sorted(os.listdir("./dilemma-fields")):
			if filename.endswith('.png'):
				file_path = os.path.join("./dilemma-fields", filename)
				images.append(imageio.imread(file_path))
		imageio.mimsave("dilema-field-evolution", images, duration=0.5)  # Adjust duration as needed

		return self

	def run(self):
		"""
		This method runs the population simulation to it's conclusion.

		Parameters
		----------
		show_steps: bool
			Displays the field at every step.
		"""
		self.spawn()
		while self.evolutions > 0:
			self.round()
			self.respawn()
			self.evolutions -= 1
		return self

def population():
	"""
	Runs population simulation with built-in bots using command line
	"""
	population_mode().run().generate_gif()
	return 0