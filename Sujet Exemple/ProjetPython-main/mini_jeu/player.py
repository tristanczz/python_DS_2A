from utils import colors
import pygame
import numpy as np

class Player:
    # height et width sont les dimensions de l'ecran du jeu
    def __init__(self, height, width, largeur, hauteur):
        self.w = width
        self.h = height
        locomotive = pygame.image.load('assets/locomotive.png')
        self.locomotive = pygame.transform.scale(locomotive, (largeur, hauteur))
        self.pos = np.array([width/2,9*height/10])
        self.largeur = largeur
        self.hauteur = hauteur
        
    def updatePos(self, action):
        #interdiction de sortir du cadre 
        self.pos[0] += action
        if self.pos[0]<0:
            self.pos[0]=0
        if self.pos[0]>self.w:
            self.pos[0]=self.w
        if self.pos[1]<0:
            self.pos[1]=0
        if self.pos[1]>self.h:
            self.pos[0]=self.h
        #print(self.pos[0])
        
    def draw(self, surface):
        surface.blit(self.locomotive, (self.pos[0] - self.largeur/2, self.pos[1] - self.hauteur/2))
        #self.blit affiche l'image qu'on lui demande à partir des coordonnées du point haut gauche de l'image
   

