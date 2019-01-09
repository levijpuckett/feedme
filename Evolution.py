#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 15:30:46 2018

@author: levipuckett
"""
import random
random.seed()
import numpy as np
from creature import Creature
from collections import Counter

def natural_selection(creatures):
    '''Creates and returns a mating pool. Mating pool consists of ever creature
    in the population, some repeated multiple times. The higher a creature's
    fitness, the more times it will appear in the gene pool, making it more 
    likely to be selected as a parent.
    @params:
        creatures: list of all creatures that have undergone the simulation.
    '''
    peak_fitness = 0
    for creature in creatures:
        if creature.nom > peak_fitness:
            peak_fitness = creature.nom
    
    mating_pool = []
    for creature in creatures:
        n = int(creature.nom / peak_fitness * 100)
        for i in range(n):
            mating_pool.append(creature)
    
    return mating_pool, Counter(mating_pool)
    
def make_babies(mating_pool, pop_size, gen, sizes, screen_size):
    '''Mix the brains of the creatures in the mating pool via crossover. return
    a list of creatures the same length as the original population.
    @params:
        mating_pool: mating pool of creatures to select from.
        pop_size: desired size of population.
    '''
    babies = []
    for i in range(pop_size - 2):
        # Randomly select two creatures from the mating pool.
        mom = mating_pool[random.randint(0,len(mating_pool)-1)]
        dad = mating_pool[random.randint(0,len(mating_pool)-1)]
        
        # Randomly mix their biases by taking a section from one parent and the
        # rest from the other.
        child_biases = []
        child_weights = []
        child_speed = 0
#        for bm,bd,wm,wd in zip(mom.biases, dad.biases, mom.weights, dad.weights):
#            cb = np.zeros_like(bm)
#            division = random.randint(0, len(bm))
#            cb[:division] = bm[:division]
#            cb[division:] = bd[division:]
#            child_biases.append(cb)
        
        # If the parents have the same sized first weight matrix, they have the
        # same eyesight. We can mix these, as well as set sizes and eyesight.
        child_speed = mom.max_speed
        wc = np.zeros_like(mom.weights[0])
        for mrow, drow, crow in zip(mom.weights[0], dad.weights[0], wc):
            division = random.randint(0, len(mrow))
            crow[:division] = mrow[:division]
            crow[division:] = drow[division:]
        child_weights.append(wc)
        # For the rest of the weights, randomly crossover genes from parents.
        for wm, wd in zip(mom.weights[1:], dad.weights[1:]):
            wc = np.zeros_like(wm)
            for mrow, drow, crow in zip(wm, wd, wc):
                division = random.randint(0, len(mrow))
                crow[:division] = mrow[:division]
                crow[division:] = drow[division:]
            child_weights.append(wc)
        
        child_weights = []
        for bm,bd,wm,wd in zip(mom.biases, dad.biases, mom.weights, dad.weights):
            cb = np.zeros_like(bm)
            cw = np.zeros_like(wm)
            division = random.randint(0, len(bm))
            cb[:division] = bm[:division]
            cb[division:] = bd[division:]
            
            cw[:division] = wm[:division]
            cw[division:] = wd[division:]
            child_weights.append(cw)
            child_biases.append(cb)
        
        # Now create the child.
        child = Creature(20,screen_size,sizes, gen, i)
        child.rebuild_brain(child_speed, child_biases, 
                            child_weights)
        babies.append(child)
    babies.append(Creature(4,screen_size, sizes, gen, pop_size - 1))
    babies.append(Creature(4,screen_size, sizes, gen, pop_size))
    return babies
    
def mutate(babies, mutation_rate):
    for baby in babies:
        for biases in baby.biases:
            for i in range(len(biases)):
                if random.random() < mutation_rate:
                    biases[i] = np.random.randn()
        for weights_matrix in baby.weights:
            for i in range(len(weights_matrix)):
                for j in range(len(weights_matrix[i])):
                    if random.random() < mutation_rate:
                        weights_matrix[i,j] = np.random.randn()
    return babies
                

def evolve_creatures(creatures, mutation_rate, gen, sizes, screen_size):
    '''Master function that implements the genetic alogrithm.'''
    mating_pool, count = natural_selection(creatures)
    babies = make_babies(mating_pool, len(creatures), gen, sizes, screen_size)
    babies = mutate(babies, mutation_rate)
    return babies
    