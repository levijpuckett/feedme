#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 17:07:01 2018

@author: levipuckett
"""
# Standard libraries.
import sys
import threading
from threading import Thread

# Third-party libraries.
import pygame as pg
pg.init()

# Other modules in this package.
import GUI, creature, Evolution

# Globals
max_speed = 15
mutation_rate = .01
creatures_per_group = 25
num_groups = 2 # Population of 50 creatures in 2 groups of 25.
num_gen = 10000
frames_per_sim = 400
ICON_SIZE = 15,15
sizes = [2,5,2]
num_foods = 300

def simulate_fast(population, clock, screen, screen_size, gen):
#    display_set = population.pop(3)
    for creature_set in population:
        thread = Thread(target=threaded_sim, args=(clock, creature_set, 
                                                   screen_size))
        thread.daemon = True
        thread.start()
    while threading.active_count() > 1:
        pg.event.pump()
        for event in pg.event.get():
            if event.type == pg.QUIT: sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    sys.exit()
    

def threaded_sim(clock, creature_set, screen_size):
    creaturelocs = [c.headbody for c in creature_set]
    env = GUI.Environment(num_foods, ICON_SIZE, creaturelocs, screen_size)
    for timer in range(frames_per_sim):
        for c in creature_set:
            foods_eaten = c.think(env.foodrects)
            if foods_eaten: 
                env.rem_food(foods_eaten)

def simulate(population, clock, screen, screen_size, gen, single,
             max_fit=None, avg_fit=None):
    for creature_set, i in zip(population,range(len(population))):
        creaturelocs = [c.headbody for c in creature_set]
        env = GUI.Environment(num_foods, ICON_SIZE, creaturelocs, screen_size)
        for timer in range(frames_per_sim):
            pg.event.pump()
            for event in pg.event.get():
                if event.type == pg.QUIT: sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        sys.exit()
            
            for c in creature_set:
                foods_eaten = c.think(env.foodrects)
                if foods_eaten: 
                    env.rem_food(foods_eaten)

            env.populate(screen, creature_set)
            
            if single:
                line1 = "Fittest creature from generation " + str(gen)
                line2 = "Fitness value: " + str(max_fit)
                line3 = "Average fitness of this generation: " + str(avg_fit)
                line4 = "Timer: " + str(frames_per_sim - timer)

                GUI.blit_text(line1, screen, topleft=(10,10))
                GUI.blit_text(line2, screen, topleft=(10,30))
                GUI.blit_text(line3, screen, topleft=(10,50))
                GUI.blit_text(line4, screen, topleft=(10,70))           
            
            else:
                line1 = "Gen: " + str(gen)
                line2 = "Group: " + str(i+1)
                line3 = "Timer: " + str(frames_per_sim - timer)

                GUI.blit_text(line1, screen, topleft=(10,10))
                GUI.blit_text(line2, screen, topleft=(10,30))
                GUI.blit_text(line3, screen, topleft=(10,50))                
            
            pg.display.flip()
            clock.tick(30)

def collect_data(population, generation):    
    length = num_groups * creatures_per_group
    tot_fit = 0
    max_fit = 0
    num_foods_eaten = 0
    best_creature = creature.Creature(0, (100,100), sizes, 0, 0)
    
    for creature_set in population:
        for c in creature_set:
            tot_fit += c.nom
            if c.nom > max_fit:
                best_creature = c
                max_fit = c.nom
                num_foods_eaten += c.num_foods_eaten

    avg_fit = tot_fit / length
    print ('GENERATION', str(generation))
    print ('Fittest creature:', best_creature.ID)
    print ('Max fitness:', best_creature.nom)
    print ('Average fitness:', avg_fit)
    print ('Number of foods eaten total:', num_foods_eaten)
    print ('Foods eaten by fittest creature:', best_creature.num_foods_eaten)
    print ()
    
    return best_creature, avg_fit

def evolve(population, generation, screen_size):
    flat_pop = []
    for creature_set in population:
        flat_pop += creature_set
    new_flat_pop = Evolution.evolve_creatures(flat_pop, mutation_rate,
                                              generation, sizes, screen_size)
    new_pop = []
    for i in range(num_groups):
        creature_set = []
        for j in range(creatures_per_group):
            creature_set.append(new_flat_pop[creatures_per_group*i + j])
        new_pop.append(creature_set)
    return new_pop

def main():
    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    screen_size = width, height = screen.get_size()

    # Start with the main menu.
    single = GUI.main_menu(screen, screen_size)
    if single:
        global creatures_per_group
        global num_groups
        global num_foods
        creatures_per_group = 1
        num_groups = 30
        num_foods = 90
    # Store the best creature and average fitness from each generation.
    best_creatures = []
    average_fitness = []
    # Create an initial, random population of creatures.
    population = []
    for i in range(num_groups):
        group = []
        for j in range(creatures_per_group):
            group.append(creature.Creature(max_speed, screen_size,
                                           sizes, 0, j+creatures_per_group*i))
        population.append(group)
    # Clock to regulate frame rate.
    clock = pg.time.Clock()
    
    if single:
        for generation in range(num_gen):
            GUI.computing_next_gen(screen, screen_size, None)
            # Simulate environment.
            simulate_fast(population, clock, screen, screen_size, generation)
            # Collect data, best/worst  creature etc.
            best_creature, avg_fit = collect_data(population, generation)
            max_fit = best_creature.nom
            best_creatures.append(best_creature)
            average_fitness.append(avg_fit)
            # Evolve creatures.
            population = evolve(population, generation, screen_size)
            # Show the best creature doing its thing.
            best_creature.num_foods_eaten = 0
            best_creature.nom = 0
            simulate([[best_creature]], clock, screen, screen_size, generation,
                     True, max_fit=max_fit, avg_fit=avg_fit)
    else:
        for generation in range(num_gen):
            # Simulate environment.
            simulate(population, clock, screen, screen_size, generation, False)
            # Collect data, best/worst  creature etc.
            best_creature, avg_fit = collect_data(population, generation)
            max_fit = best_creature.nom
            best_creatures.append(best_creature)
            average_fitness.append(avg_fit)
            # Evolve creatures.
            population = evolve(population, generation, screen_size)

if __name__ == "__main__":
    main()

    
    
    
    
    
    
    
    
    
    
    
