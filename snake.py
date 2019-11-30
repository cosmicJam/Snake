
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

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

# TODO
# Reading in locations of snack?
data = []


# Problem parameters
NUM_DIRECT = 10            # number of directions in a given individual


# algorithm parameters
CXPB = 0.9                 # probability that two selected individuals will recombine
GENS = 100  		 	   # number of generation in the run
POP_SIZE = 100        	   # number of individuals
ELITE_NUM = 10
TOURN_SIZE = 4
HOF_SIZE = 5               # number of best members in hall of fame
MUTPB = 0.7



# print column headings for the output log
def print_logbook_header():
    print("{:>6}{:>8}{:>12}{:>12}{:>12}{:>12}".format("gen", "nevals", "avg", "std", "min", "max"))
    

# print a single data row from the output log
# one row represents one generation of the GA run
def print_logbook_row(r):
    print("{:>6}{:>8}{:>12.4}{:>12.4}{:>16}{:>16}".format(r['gen'], r['nevals'],
                                                        r['Avg'], r['Std'],
                                                        r['Min'], r['Max']))



# FITNESS FUNCTION #TODO
def eval_(indiv):


# MUTATION #TODO
def mutation(individual, indpb):


#TODO
def get_direct():



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
        # offspring = toolbox.clone(population)
        
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
        # currently chooses ELITE_NUM best individuals and fills rest of
        # next_pop with individuals chosen at random
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
toolbox.register("genome", tools.initRepeat, list, toolbox.direction, NUM_POINTS)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.genome)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", eval_)
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", mutation, indpb=0.75/NUM_POINTS)
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

    unit_circle(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=GENS, stats=stats,
                                                            halloffame=hof, verbose=True)
    return pop, stats, hof


if __name__ == "__main__":
    # call to main program
    # change the parameter (seed for random) to a constant for repeatability
    _, _, hof = main(time())
    
    print
    
    # output individuals from hall of fame
    for indiv in hof:
#        print('{}  {}'.format(COMPLETE WITH VALUES APPROPRIATE TO YOUE SOLUTION))
        print('{}\n'.format(indiv))
