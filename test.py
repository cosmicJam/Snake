import game
import random



def print_outcome(result):
	if result[0] == -1: print("Escape key pressed")
	elif result[0] == -2: print("No more moves")
	elif result[0] == -3: print("Collision encountered")
	elif result[0] == -4: print("Player is stuck")
	elif result[0] == 0: print("Success!")
	print("Score: " + str(result[1]))
	print("Time:  " + str(result[2]))

actions_test = [1,1,1,1,1,3,3,3,3,3,3,0,2,1,1]
actions = [random.randrange(4) for i in range(1000)]

app = game.App()

#
# Mode 1: Full run
#

#result = app.run(
#	actions = actions,
#	clock = app.WARP, # VERY_SLOW, SLOW, NORMAL, FAST, VERY_FAST, WARP, NO_CLOCK
#	map_size = 10,
#	square_size = 20,
#	random_food = False,
#	end_on_collisions = True,
#	wait_on_end = False,
#	verbose = False
#)
#print_outcome(result)

#result = app.run(
#	actions = actions,
#	clock = app.WARP,
#	map_size = 10,
#	square_size = 20,
#	random_food = False,
#	end_on_collisions = False,
#	wait_on_end = False,
#	verbose = True
#)
#print_outcome(result)

#
# Mode 2: Run at each step()
# (Use if you want to ensure that the genome disallows poor moves, by
#  evaluating the map after each step)
#

app.start(
	clock = app.WARP,
	map_size = 5,
	square_size = 20,
	random_food = False,
	end_on_collisions = False,
	wait_on_end = False,
	verbose = False
)

result = None
for i in range(0, len(actions)):
	result = app.step(actions[i])
	if result[0] != -2:
		break
print_outcome(result)