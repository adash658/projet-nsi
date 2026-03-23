import pygame
from sources.constants import *

class NPC:
    def __init__(self, name, x, y, etat_depart="ID"):
        self.name = name

        self.rect = pygame.Rect(0, 0, 48, 16) 
        self.rect.midbottom = (x, y)

        self.portraits = {}
        emotions = ["angry", "happy", "neutral", "sad"]
        for emotion in emotions:
            try:
                chemin = f"assets/pnj/{self.name.capitalize()}/{emotion}.png"
                img = pygame.image.load(chemin).convert_alpha()
                self.portraits[emotion] = pygame.transform.scale_by(img, 1)
            except FileNotFoundError:
                pass

        self.animations = {'ID': [], 'IR': [], 'IL': [], 'IU': [], 'R': [], 'L': [], 'U': [], 'D': []}
        self.state = etat_depart
        self.current_frame = 0
        self.animation_speed = 0.15
        
        dossier_pnj = f"assets/pnj/{self.name.capitalize()}/"

        for direction in ['ID', 'IR', 'IL', 'IU']:
            try:
                img = pygame.image.load(dossier_pnj + f"{direction}.png").convert_alpha()
                self.animations[direction].append(pygame.transform.scale_by(img, 4))
            except FileNotFoundError:
                pass

        for direction in ['R', 'L', 'U', 'D']:
            for i in range(1, 5):
                try:
                    img = pygame.image.load(dossier_pnj + f"{direction}{i}.png").convert_alpha()
                    self.animations[direction].append(pygame.transform.scale_by(img, 4))
                except FileNotFoundError:
                    pass

        if self.state in self.animations and len(self.animations[self.state]) > 0:
            self.image = self.animations[self.state][0]
        else:
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 255)) 

        self.chemin = []
        self.vitesse = 2.6
        self.draw_offset_y = -76
        
    def draw(self, screen, camera_x, camera_y):
        npc_rect_screen = self.rect.copy()
        npc_rect_screen.x -= camera_x
        npc_rect_screen.y -= camera_y

        image_rect = self.image.get_rect(
            midbottom=(npc_rect_screen.centerx, npc_rect_screen.bottom - self.draw_offset_y)
            )
        screen.blit(self.image, image_rect)

    def donner_chemin(self, points):
        self.chemin = points
    
    def suivre_chemin(self):
        if not self.chemin:
            if self.state == 'R': self.state = 'IR'
            elif self.state == 'L': self.state = 'IL'
            elif self.state == 'U': self.state = 'IU'
            elif self.state == 'D': self.state = 'ID'
            return True

        cible_x, cible_y = self.chemin[0]

        if abs(self.rect.x - cible_x) > self.vitesse:
            if self.rect.x < cible_x: 
                self.rect.x += self.vitesse
                self.state = 'R'
            elif self.rect.x > cible_x: 
                self.rect.x -= self.vitesse
                self.state = 'L'

        elif abs(self.rect.y - cible_y) > self.vitesse:
            if self.rect.y < cible_y: 
                self.rect.y += self.vitesse
                self.state = 'D'
            elif self.rect.y > cible_y: 
                self.rect.y -= self.vitesse
                self.state = 'U'
                
        else:
            self.rect.x = cible_x
            self.rect.y = cible_y
            self.chemin.pop(0)

            if not self.chemin:
                map_idle = {'R': 'IR', 'L': 'IL', 'U': 'IU', 'D': 'ID'}
                self.state = map_idle.get(self.state, 'ID')
                return True
            
        return False

    def animate(self):
        frames = self.animations.get(self.state, [])
        if len(frames) > 0:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(frames):
                self.current_frame = 0
                
            self.image = frames[int(self.current_frame)]