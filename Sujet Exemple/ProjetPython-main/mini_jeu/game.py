import os
#os.environ["SDL_VIDEODRIVER"] = "dummy"
from os import remove
from utils import colors, sp
import pygame
from player import Player
from projectiles import Projectiles, Projectile
import time
import numpy as np
import sys 

#Création de la classe world, base du jeu
class world:
    def __init__(self, generationRate=0.1, nombreProjectilesMax=8, width=480, height=640):
        self.w = width
        self.h = height
        self.player = Player(height, width, 70, 40)
        self.projectiles = Projectiles(generationRate, nombreProjectilesMax, width, height)
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Train')
        self.clock = pygame.time.Clock()
        
    def _update_ui(self):
        self.display.fill(colors.GREY)
        self.player.draw(self.display)
        self.projectiles.draw_projectiles(self.display)
        pygame.display.flip()
    
    def play_step_and_draw(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        action = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            action = -10
        if keys[pygame.K_RIGHT]:
            action = 10

        #Update des positions du train et des projectiles        
        self.player.updatePos(action)
        self.projectiles.update()
        gameOver = self.projectiles.gameOver(self.player)

        self._update_ui()
        self.clock.tick(sp.SPEED)
         
        return gameOver


if __name__ == '__main__':
    game = world()
    
    #game loop
    while True:
        game_over = game.play_step_and_draw()
        
        if game_over == True:
            break     #si game over, le jeu est fini
    pygame.quit()
    
    
    