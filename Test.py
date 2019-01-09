#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 17:32:43 2018

@author: levipuckett
"""
import pygame as pg
pg.init()
pg.font.init()
import GUI, sys, creature, Evolution

speed = [2, 2]
black = 0,0,0
green = 0,255,0
blue = 0,0,255
red = 255,0,0
white = 255,255,255

screen = pg.display.set_mode((0,0),pg.FULLSCREEN)
screen_size = width, height = screen.get_size()
mutation_rate = .01

tests = []

for i in range(6):
    c = []
    for j in range(10):
        c.append( creature.Creature(5, 30, screen_size, [8,2], 0, i, simple=True) )
    tests.append(c)
clock = pg.time.Clock()
GUI.main_menu(screen, screen_size)
for generation in range(10000):
    for creature_set, i in zip(tests,range(len(tests))):
        creaturelocs = [i.headbody for i in creature_set]
        env = GUI.Environment(200, 30, (15,15), creaturelocs, screen_size)
        for timer in range(500):
            font = pg.font.SysFont('Comic Sans MS', 30)
            string = "Gen: " + str(generation) + ", group: " + str(i+1)
            string += ", timer: " + str(500 - timer)
            fontsurf = font.render(string, False, black)
            startrect = fontsurf.get_rect(topleft=(0,0))
            
            pg.event.pump()
            for event in pg.event.get():
                if event.type == pg.QUIT: sys.exit()
                if event.type == pg.MOUSEMOTION:
                    mouse_pos = pg.mouse.get_pos()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        sys.exit()

            env.populate(screen)

            for c in creature_set:
                if not c.dead:
                    foods_eaten, dead = c.think_simple(env.foodrects, env.dangerrects, width, height)
                    if dead:
                        env.add_corpse(c.headbody.center)
                    if foods_eaten: 
                        env.rem_food(foods_eaten)
                    c.animate(screen)
            screen.blit(fontsurf, startrect)
            pg.display.flip()
            clock.tick()
    length = 0
    for creature_set in tests:
        length += len(creature_set)
    tot_fit = 0
    max_fit = 0
    num_foods_eaten = 0
    max_fit_foods = 0
    best_creature = ""
    for test in tests:
        for c in test:
#        print (test.biases)
            tot_fit += c.nom
            if c.nom > max_fit:
                max_fit = c.nom
                max_fit_foods = c.num_foods_eaten
                best_creature = c.ID
                num_foods_eaten += c.num_foods_eaten
    print ('GENERATION', str(generation))
    print ('Fittest creature:', best_creature)
    print ('Max fitness:', max_fit)
    print ('Average fitness:', tot_fit / length)
    print ('Number of foods eaten total:', num_foods_eaten)
    print ('Foods eaten by fittest creature:',max_fit_foods)
    print ()
    
    flatten = []
    for i in tests:
        flatten += i
    new_tests = Evolution.evolve_creatures(flatten, mutation_rate, generation)
    tests = []
    for i in range(6):
        c = []
        for j in range(10):
            c.append(new_tests[10*i + j])
        tests.append(c)
    











