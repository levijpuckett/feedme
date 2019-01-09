#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 21:00:37 2018

@author: levipuckett
"""

import pygame as pg
import random, sys
pg.font.init()

# Define colours.
BLACK = 0,0,0
WHITE = 255,255,255
RED = 255,0,0
GREEN = 0,255,0
GRASS = 0,100,0
BLUE = 0,0,255
BACKGROUND = 200,200,150

# Food and danger icons.
food_icon = "icons/lettuce1.png"
danger_icon = "icons/fire1.png"
death_icon = "icons/skull.png"

def blit_text(text, surface, colour=BLACK, size=30, **args):
    '''Renders the text and blits it onto the given surface.'''
    font = pg.font.SysFont('Times', size)
    fontsurf = font.render(text, False, colour)
    fontrect = fontsurf.get_rect(**args)
    surface.blit(fontsurf, fontrect)

def render_text(text, colour=BLACK, size=30, **args):
    '''Renders the text and returns a surface and a rect, ready to be blit.'''
    font = pg.font.SysFont('Times', size)
    fontsurf = font.render(text, False, colour)
    fontrect = fontsurf.get_rect(**args)
    return (fontsurf, fontrect)

def main_menu(surface, screen_size):
    '''Simple entry point to app. Gives details about the project and
    provides a start button.
    '''
    menu = True
    main_menu_text = render_text("feedme", size=70, 
                                 center=(screen_size[0]/2,screen_size[1]*1/4))
    start_sim_text1 = render_text("START - ONE CREATURE AT A TIME", size=50, 
                                 center=(screen_size[0]/2,screen_size[1]/2))
    start_rect1 = start_sim_text1[1]
    start_colour1 = GRASS
    start_colour2 = GRASS

    start_sim_text2 = render_text("START - MULTIPLE CREATURES AT ONCE", size=50, 
                                 center=(screen_size[0]/2,screen_size[1]/2+100))
    start_rect2 = start_sim_text2[1]
    
    author_text = render_text("Levi Puckett, 2018", size=22,
                              center=(screen_size[0]/2,screen_size[1]*9/10))
    
    while menu:
        pg.event.pump()
        for event in pg.event.get():
            if event.type == pg.QUIT: sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE: sys.exit()
        
        start_collide1 = start_rect1.collidepoint(pg.mouse.get_pos())
        start_collide2 = start_rect2.collidepoint(pg.mouse.get_pos())
        mouse1, mouse2, mouse3 = pg.mouse.get_pressed()
        if start_collide1 and mouse1:
            return True
        elif start_collide1:
            start_colour1 = GREEN
        elif start_collide2 and mouse1:
            return False
        elif start_collide2:
            start_colour2 = GREEN
        else:
            start_colour1 = start_colour2 = GRASS
        
        surface.fill(BACKGROUND)
        surface.blit(main_menu_text[0],main_menu_text[1])
        pg.draw.rect(surface, start_colour1, start_rect1)
        pg.draw.rect(surface, start_colour2, start_rect2)
        surface.blit(start_sim_text1[0], start_sim_text1[1])
        surface.blit(start_sim_text2[0], start_sim_text2[1])
        surface.blit(author_text[0], author_text[1])
        pg.display.flip()
        
def computing_next_gen(surface, screen_size, progress):
    '''Simple 'loading screen' '''
    loading_text = render_text("Preparing next generation...", size=70, 
                                 center=(screen_size[0]/2,screen_size[1]*1/4))
    loading_rect = loading_text[1]
    
    surface.fill(GRASS)
    surface.blit(loading_text[0],loading_text[1])
    pg.display.flip()
        
class Sidebar():
    '''Hold statistics about the simulation in the sidebar. Handles printing
    all text on sidebar.
    '''
    
class Environment():
    '''Holds information about the current simulation's environment.'''
    def __init__(self, num_food, icon_size, creatures, screen_size):
        '''Initialize the environment.
        @params:
            num_food: number of food items to be in environment at start.
            num_danger: number of danger items to be in environment at start.
            icon_size: two-tuple, width and height of icon.
            screen_size: two-tuple, max (x,y) coordinates allowed by screen.
        '''
        self.env_surf = pg.Surface((int(screen_size[0]),int(screen_size[1])))
        self.env_surf.fill(GRASS)
        self.env_rect = self.env_surf.get_rect()
        self.env_size = self.env_rect.size
        
        self.colour = GRASS
        self.num_food = num_food

        self.dead = pg.image.load(death_icon)
        self.dead = pg.transform.scale(self.dead, icon_size)
        self.deadrects = []
        
        self.food = pg.image.load(food_icon)
        self.food = pg.transform.scale(self.food, icon_size)
        
        #make list to store various food rects. randomly assign.
        self.foodrects = []
        for i in range(num_food):
            rect = self.avoid_collisions(self.food, creatures, screen_size, icon_size)
            if rect:
                self.foodrects.append(rect)
        
    def avoid_collisions(self, item, creatures, screen_size, icon_size):
        '''Function to guarantee items are not spawned on top of creatures
        directly. Returns a rect object with non-collision coordinates.
        @params:
            items: items to avoid spawning on creatures.
            creatures: list of creatures in simulation environment.
        '''
        colliding = True
        while colliding:
            coordinates = (random.randint(0, self.env_size[0] - icon_size[0]),
                           random.randint(0, self.env_size[1] - icon_size[1]))
            rect = item.get_rect(center=coordinates)
            collision = rect.collidelist(creatures)#[i.colliderect(rect) for i in creatures]
            if collision != -1:
                return None
            colliding = False
        return rect
    
    def populate(self, surface, creatures):
        '''Populate the surface with environment details.'''
        self.env_surf.fill(GRASS)
        for foodrect in self.foodrects:
            self.env_surf.blit(self.food, foodrect)
        for c in creatures:
            c.animate(self.env_surf)
        surface.blit(self.env_surf, self.env_rect)
    
    def add_corpse(self, coords):
        '''Add another one to the pile.'''
        self.deadrects.append(self.dead.get_rect(center=coords))
        
    def rem_food(self, foods_eaten):
        '''Remvoe eaten food from environment food list.'''
        for food in foods_eaten:
            self.foodrects.remove(food)

def main():    
    main_menu()
    
if __name__ == "__main__":
    main()
