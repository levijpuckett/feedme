#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 21:22:51 2018

@author: levipuckett

Implements creature class. Gives creatures a brain and animation.
"""
import numpy as np
import pygame as pg
import random, math

SEE_COLOUR = 0,0,0
CREATURE_SIZE = 16 # Even number.
TRANSPARENCY = 50
class Brain():
    '''Creature brain. Includes thinking for free!'''
    def __init__(self, sizes, weights=None, biases=None):
        self.number_of_layers = len(sizes)
        self.sizes = sizes
        
        #Build weights array.
        #List filled with 2D Numpy arrays.
        #Each entry in the list is a layer.
        #Each row indicates node in current layer,
        #each column indicates link to previous layer's node.
        #so self.weights[0][2,3] is layer 1: connection between
        #layer 1, node 2 and layer 0 (input), node 3.
        if weights:
            self.weights = weights
        else:
            self.weights = [ np.random.randn(x,y)
                            for x,y in zip(sizes[1:],sizes[:-1]) ]            

        #Build weights array.
        #list filled with Numpy vectors.
        #Each entry in the list is a layer.
        #each component of the vector is the 
        #bias of that node in the layer.
        #self.biases[2][1] is the bias of
        #node 1 in layer 2.
        if biases:
            self.biases = biases
        self.biases = [ np.random.randn(x)
                        for x in sizes[1:]]

    def feedforward(self, x):
        '''Feed the input x forward through the network. Returns output.'''
        # First layer activation is input.
        activation = x
        
        for w,b in zip(self.weights, self.biases):
            z = np.dot(w, activation) + b
            activation = self.sigmoid(z)
        return activation
    
    def sigmoid(self, z):
        '''Returns a 'squished' z vector according to:
            sig = 1 / (1 + e^(-z))
        returns as numpy array.
        '''
        return (2.0 / (1.0 + np.exp(-z))) - 1
    
class Animation():
    '''Animation for creature. Stores coordinates, rects,
    and surfaces to blit.
    '''
    def __init__(self, screen_size):
        # Randomly initialize starting coordinates.
        coords = np.array([random.randint( 0 ,screen_size[0] - CREATURE_SIZE ),
                       random.randint( 0 ,screen_size[1] - CREATURE_SIZE )])

        # Random, non-green colour to identify the creature on-screen.
        self.colour = random.randint(0,255), 0, random.randint(0,255)
        
        # Make a Rect object for the creature.
        # This Rect object stores information about the creature's location.
        self.headbody = pg.Rect(coords, (CREATURE_SIZE, CREATURE_SIZE))
        self.headbodysurf = pg.Surface((self.headbody.size))
        self.headbodysurf.fill(self.colour)

        
    def move(self, speed):
        '''Move the creature through one frame of animation. Also updates
        current coordinates.
        @params:
            speed: speed of creature for this frame. Numpy array.
        '''
        self.headbody = self.headbody.move(speed)
        if self.headbody.left < 0:
            self.move((-self.headbody.left, 0))
        if self.headbody.right > self.coords_max[0]:
            self.move((self.coords_max[0] - self.headbody.right,0))
        if self.headbody.top < 0:
            self.move((0,-self.headbody.top))
        if self.headbody.bottom > self.coords_max[1]:
            self.move((0, self.coords_max[1] - self.headbody.bottom))
        
    def animate(self, surface):
        '''Draw the creature on the given surface as-is.'''
        surface.blit(self.headbodysurf, self.headbody)

class Creature(Brain, Animation):
    '''Instantiates a creature. Creatures have brains and animations.'''
    def __init__(self, speed_max, coords_max, sizes, gen, inst):
        '''Initializes a creature randomly. uses speed_range to randomly 
        generate a max speed value.
        @params:
            speed_max: Highest allowed integer speed in this simulation.
            coords_max: Two-tuple of highest allowed starting coordinates.
            trunc_sizes: Neural network size. Length of array indicates number of
                layers, the value of each index indicates the number of nodes
                in each layer. First layer determined by eyesight, not passed
                into this initializing function.
        '''
        self.ID = str(gen) + '.' + str(inst)
        self.gen = gen
        self.inst = inst
        self.coords_max = coords_max
        # IT'S ALIVE
        self.dead = False
        # Initialize fitness function to zero.
        self.nom = 0.0
        self.num_foods_eaten = 0
        # Set max speed.
        self.max_speed = speed_max

        # Initialize brain.
        self.sizes = sizes
        Brain.__init__(self, self.sizes)
        # Initialize animation.
        Animation.__init__(self, self.coords_max)
        
    def rebuild_brain(self, max_speed, biases, weights):
        '''This modifies the randomly created creature into something
        resembling its parents. Must be called just after birth.
        @params:
            max_speed: max speed from either the mother or father.
            eyesight: eyesight of mother and father (must be the same).
            sizes: corrects size of the brain's input layer.
            biases: part of the genetic code, mix of mother and father.
            weights: part of the genetic code, mix of mother and father.
        '''
        self.max_speed = max_speed
        
        Brain.__init__(self, self.sizes, weights=weights, biases=biases)
        Animation.__init__(self, self.coords_max)
    
    def _calc_distance(self, p1, p2):
        '''Finds the shortest distance between two points on a plane.'''
        return math.sqrt(abs(p1[0] - p2[0])**2 + abs(p1[1] - p2[1])**2)
    
    def _calc_fitness(self, foods, num_foods_eaten, max_dist):
        '''Modifies the creature's nom score based on the number of eaten 
        foods and the closest food to it. Closest food does not need to be in
        sight.
        @params:
            foods: all foods in environment.
            num_foods_eaten: number of foods eaten in the previous frame.
        '''
        self.nom = num_foods_eaten ** 2
        
    def find_nearest_item(self, items):
        '''Simple function to find the nearest item in a list of pygame rects.
        returns the coordinates of the item, and the distance to it.
        '''
        nearest_item_dist = 1000000000
        nearest_item_coords = (0,0)
        for item in items:
            cur_dist = self._calc_distance(item.center, self.headbody.center)
            if cur_dist < nearest_item_dist:
                nearest_item_dist = cur_dist
                nearest_item_coords = item.center
        return nearest_item_dist, nearest_item_coords
        
    def _danger_mod(self, x):
        return (1 / (1 + math.exp(-(x-20)))) + (1 / (1 + math.exp(x+20)))
    
    def think(self, foods, dangers=None, neighbours=None):
        '''Simpler implementation of sight. In this case, the creatures are
        told how far away the nearest food and danger are from them. This makes
        the input to the network 4 integers, instead of up to 5000.
        @params:
            foods: list of all food rects in the environment.
            dangers: optional argument, list of all danger rects in the
            environment.
            neighbours: optional argument for a future predation implementation
        returns:
            foods_eaten: a list of foods that the creature ate this frame.
            self.dead: a boolean that indicates whether the creature is alive.
        '''
        # Find the nearest food.
        food_dist, food_coords = self.find_nearest_item(foods)
        # Modify coords to be (x,y) distance from center of creature's headbody.
        food_coords = (food_coords[0] - self.headbody.centerx, 
                       food_coords[1] - self.headbody.centery)

        food_coords = ( food_coords[0]/(1+abs(food_coords[0])),
                       food_coords[1]/(1+abs(food_coords[1])))

        brain_input = np.array(food_coords)
        speed = self.max_speed * self.feedforward(brain_input)
        
        self.move(speed)
        
        foods_eaten = [foods[i] for
                       i in self.headbody.collidelistall(foods)]
        self.num_foods_eaten += len(foods_eaten)

        self._calc_fitness(foods, self.num_foods_eaten, 
                           self._calc_distance(self.coords_max,(0,0)))
        return foods_eaten
            
            
            
            
            
         
