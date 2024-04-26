import numpy as np

def tit_for_tat(opponent_moves):
    """
    Player that copies opponents last move.

	Parameters
	----------
	opponent_moves: nested list structure
		Player algorithm.
    """
    ii = len(opponent_moves)
    if ii == 0:
        return True
	
    return opponent_moves[ii-1][1]
    
def always_defect(opponent_moves):
	"""
	Player always defects.

	Parameters
	----------
	opponent_moves: nested list structure
		Player algorithm.
	"""
	return False

def always_cooperate(opponent_moves):
	"""
	Player always cooperates.

	Parameters
	----------
	opponent_moves: nested list structure
		Player algorithm.
	"""
	return True

def tester(opponent_moves):
	"""
	Player first plays defect. If the opponent plays cooperate, tester will 
	apologize by playing cooperate twice. After apologizing, or if the opponent
	opens with defect, tester will play tit-for-tat.

	Parameters
	----------
	opponent_moves: nested list structure
		Player algorithm.
	"""

	ii = len(opponent_moves)

	# copperate -> defect -> cooperate -> cooperate
	if ii == 0:
		return True

	if ii == 1:
		return False

	if ii in range(2, 3):
		return True
	
	# If opponent did not retaliate, always defect. If opponent retaliated, play copycat.
	if opponent_moves[2]:
		return False

	return opponent_moves[ii-2][1]

def grudge(opponent_moves):
	"""
	Player cooperates until the opponent defects. Once the opponent defects,
	player always defect.

	Parameters
	----------
	opponent_moves: nested list structure
		Player algorithm.
	"""

	ii = len(opponent_moves)
	if ii == 0:
		return True

	for move in opponent_moves:
		if not move[1]:
			return False

	return True

def random(_):
	"""
	Player chooses randomly to cooperate or defect. Ignores input.
	"""

	return np.random.default_rng().integers(0, 1, endpoint=True)

def weighted_guess(opponent_moves):
	"""
	Player first plays cooperate. Then, makes a semi-random choice to defect
	or cooperate weighted by the number of opponent cooperations. Will
	cooperate more often if the opponent cooperates more often.

	Parameters
	----------
	opponent_moves: nested list structure
		Player algorithm.
	"""
	
	ii = len(opponent_moves)

	# First move is cooperate
	if ii == 0:
		return True
	
	# Determine the fraction of total cooperations
	coop_frac = 0

	for move in opponent_moves:
		if move[1]:
			coop_frac += 1/ii
		
	# Make a random choice, then compare that to the fraction of cooperations
	random_choice = np.random.default_rng().random()

	if random_choice < coop_frac:
		return True
	return False


