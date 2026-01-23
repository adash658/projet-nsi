import pygame
import os

class Player:
    def __init__(self, x, y):
        self.posix = x
        self.posiy = y
        self.speed = 2
        self.ispaused = False

        self.base_w, self.base_h = 48, 64
        self.scale_factor = 2

        self.direction = "down"
        self.state = "Idle"
        self.frame_index = 0
        self.anim_speed = 0.2
        
        self.animations = {"Idle": {}, "Walk": {}}
        self.load_images()
        
        self.image = self.animations["Idle"]["down"][0]
        self.rect = self.image.get_rect(center=(x, y))

    def load_images(self):
            for state in ["Idle", "Walk"]:
                for direction in ["up", "down", "left", "right"]:
                    path = f"assets/player/{state}/{state.lower()}_{direction}.png"
                    
                    if os.path.exists(path):
                        strip = pygame.image.load(path).convert_alpha()
                        frames = []
                        for x in range(0, strip.get_width(), self.base_w):
                            rect = pygame.Rect(x, 0, self.base_w, self.base_h)
                            frame = strip.subsurface(rect)
                            scaled_frame = pygame.transform.scale_by(frame, self.scale_factor)
                            frames.append(scaled_frame)
                        self.animations[state][direction] = frames

    def move(self):
        if self.ispaused: return

        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT]:
            self.posix -= self.speed
            self.direction, moving = "left", True
        elif keys[pygame.K_RIGHT]:
            self.posix += self.speed
            self.direction, moving = "right", True
        elif keys[pygame.K_UP]:
            self.posiy -= self.speed
            self.direction, moving = "up", True
        elif keys[pygame.K_DOWN]:
            self.posiy += self.speed
            self.direction, moving = "down", True

        self.state = "Walk" if moving else "Idle"
        
        self.animate()
        self.rect.center = (self.posix, self.posiy)

    def animate(self):
        """ Fait défiler les images """
        current_anim = self.animations[self.state][self.direction]
        
        # On augmente l'index
        self.frame_index += self.anim_speed
        
        # Si on dépasse le nombre d'images, on revient à 0
        if self.frame_index >= len(current_anim):
            self.frame_index = 0
            
        # On prend l'image (l'index devient un nombre entier : 0, 1, 2...)
        self.image = current_anim[int(self.frame_index)]

    def lock(self): 
        self.ispaused = True
    def unlock(self): 
        self.ispaused = False