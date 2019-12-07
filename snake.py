""" TODO
	-Write operators that work for random food locations
		-Fitness: Take minimum across 10+ runs (prioritize solutions which work
		          generally
	-Allow game to return a new list of actions that skips over invalid actions,
	 then replace the individual with that
	-

"""

"""
    Genetic algorithm template for the snake game
    
    
    Implemented using DEAP
    
    
	Teresa Muellenbach
	Nickolas Hexum
	Tyler Landowski
	Jamie Vue	
    November 2019
    
"""


import random
import numpy
import game
import math

from datetime import datetime

from deap import algorithms
from deap import base
from deap import creator
from deap import tools


# TODO
# Reading in locations of snack?
data = []

SHOW_TRAINING = False

# Problem parameters

# num_spaces = GRID_SIZE^2
GRID_SIZE = 5
# number of actions/alleles
NUM_ACTIONS = 1000
# number of directions in a given individual
NUM_DIRECT = 4
# whether food positions are random or not
RANDOM_FOOD = False
# end game as soon as snake dies, or skip poor actions (still counts as move)
END_ON_COLLISIONS = False
# Fitness penalty for every action taken
TIME_PENALTY = 0.001

# algorithm parameters
CXPB = 0.9                 # probability that two selected individuals will recombine
GENS = 100  		 	   # number of generation in the run
POP_SIZE = 100        	   # number of individuals
ELITE_NUM = 10
TOURN_SIZE = 4
HOF_SIZE = 5               # number of best members in hall of fame
MUTPB = 0.7

app = game.App()


# print column headings for the output log
def print_logbook_header():
    print("{:>6}{:>8}{:>12}{:>12}{:>12}{:>12}".format("gen", "nevals", "avg", "std", "min", "max"))
    

# print a single data row from the output log
# one row represents one generation of the GA run
def print_logbook_row(r):
    print("{:>6}{:>8}{:>12.4}{:>12.4}{:>16}{:>16}".format(r['gen'], r['nevals'],
                                                        r['Avg'], r['Std'],
                                                        r['Min'], r['Max']))

# Replace the move that ended in death, and a number of moves before that
def mutation_replace_end(individual, indpb=-1):
	# Get last action
	last_action = len(individual) - 1
	for i in range(0, len(individual)):
		if individual[i] == -1:
			last_action = i
	
	# number of actions to replace
	to_replace = random.randrange(1, 16, 1)
		
	for i in range(max(last_action - to_replace, 0), len(individual), 1):
		individual[i] = random.randrange(NUM_DIRECT)
	
	return individual,

def mutation(individual, indpb=-1):
	return individual,

def mutation_null(individual, indpb):
	pass
	#return individual,

def crossover_null(ind1, ind2):
	return (ind1, ind2)

def get_direct():
	return random.randrange(NUM_DIRECT)
	
def evaluate(individual):
	clock = app.NO_CLOCK
	if SHOW_TRAINING: clock = app.LIGHT
	result = app.run(
		actions = list(individual), # Check this line for performance
		clock = clock,
		map_size = GRID_SIZE,
		random_food = RANDOM_FOOD,
		end_on_collisions = END_ON_COLLISIONS,
	    verbose = False,
        wait_on_end = 0
	)
	score = result[1]
	moves = result[2]
	
	# Distance from food (from 1 to (GRID_SIZE-1)*2)
	dist_from_food = app.manhattan_dist()
	bonus = 1 - (dist_from_food / ((GRID_SIZE - 1) * 2))
	penalty = moves * TIME_PENALTY
	
	# Also, mark every action not taken with -1
	for i in range(moves, len(individual)):
		individual[i] = -1
	
	return (score + bonus - penalty,)

# main function
def snake(population, toolbox, cxpb, mutpb, ngen, stats=None,
             halloffame=None, verbose=False):
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    for ind in population:
        del ind.fitness.values
    fitnesses = toolbox.map(toolbox.evaluate, population)
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(population), **record)

    if verbose:
        print_logbook_header()
        print_logbook_row(logbook[0])
    
    # Begin the generational process
    for gen in range(1, ngen + 1):
        
        # Select individuals to serve as parents by copying current parent population
        offspring = toolbox.clone(population)
        
        # use the defined select method to choose parents.
        offspring = toolbox.clone((toolbox.select(population)))
        
        # crossover
        for child1, child2 in zip(offspring[0::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
                
        # mutation
        for mutant in offspring:
            toolbox.mutate(mutant)
            del mutant.fitness.values
        
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)
        
        # replacement
        #currently chooses ELITE_NUM best individuals and fills rest of
        #next_pop with individuals chosen at random
        population.extend(offspring)
        next_pop = toolbox.replace(population, POP_SIZE - ELITE_NUM)
        elite = toolbox.elite(population, ELITE_NUM)
        next_pop.extend(elite)
        population = toolbox.clone(next_pop)
        
        random.shuffle(population)
        
        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        
        if verbose:
            print_logbook_row(logbook[gen])

    return population, logbook


# YOU WILL CHANGE EVERYTHING IN THIS SECTION
# create the DEAP structures
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# THIS IS WHERE YOU CREATE THE REPRESENTATION
#Structure initializers
toolbox.register("direction", get_direct)
toolbox.register("genome", tools.initRepeat, list, toolbox.direction, NUM_ACTIONS)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.genome)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate)
#toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mate", crossover_null)
#toolbox.register("mutate", mutation_null, indpb=0.75/NUM_ACTIONS)
toolbox.register("mutate", mutation_replace_end)
#toolbox.register("mutate", mutation, indpb=0.75/NUM_ACTIONS)
# method for parent selection
toolbox.register("select", tools.selTournament, k=POP_SIZE, tournsize=TOURN_SIZE)
# method for survival selection
toolbox.register("replace", tools.selRandom)
toolbox.register("elite", tools.selBest)


def main(seed):
    random.seed(seed)

    pop = toolbox.population(n=POP_SIZE)
    hof = tools.HallOfFame(HOF_SIZE)
    # UPDATE PARAMETER IN FOLLOWING LINE AS NECESSARY
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("Avg", numpy.mean)
    stats.register("Std", numpy.std)
    stats.register("Min", numpy.min)
    stats.register("Max", numpy.max)

    snake(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=GENS, stats=stats,
                                                            halloffame=hof, verbose=True)
    return pop, stats, hof


if __name__ == "__main__":
    # call to main program
    # change the parameter (seed for random) to a constant for repeatability
    _, _, hof = main(datetime.now())
    
    # output individuals from hall of fame
    for indiv in hof:
        #print('{}\n'.format(indiv))
        print("Showing best individuals...")
        result = app.run(
            actions = indiv,
            clock = app.WARP,
            map_size = GRID_SIZE,
            random_food = RANDOM_FOOD,
            end_on_collisions = END_ON_COLLISIONS,
            wait_on_end = 1000,
            verbose = True
        )