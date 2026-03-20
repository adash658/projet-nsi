import pygame
import os


class Player:
    def __init__(self, x, y):
        self.posix = x
        self.posiy = y
        self.speed = 3
        self.ispaused = False

        self.base_w, self.base_h = 48, 64
        self.scale_factor = 1

        self.direction = "down"
        self.state = "Idle"
        self.frame_index = 0
        self.anim_speed = 0.16

        self.animations = {"Idle": {}, "Walk": {}}
        self.load_images()

        self.image = self.animations["Idle"]["down"][0]
        self.rect = pygame.Rect(0, 0, 48, 16) 
        self.rect.center = (x, y)

    def load_images(self):
        direction_map = {"down": "D", "left": "L", "right": "R", "up": "U"}

        self.animations["Idle"] = {}
        for direction, code in direction_map.items():
            path = f"assets/player/Idle/I{code}.png"
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.animations["Idle"][direction] = [pygame.transform.scale_by(img, self.scale_factor)]

        self.animations["Walk"] = {}
        for direction, code in direction_map.items():
            frames = []
            for i in range(1, 5):
                path = f"assets/player/Walk/{code}{i}.png"
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    frames.append(pygame.transform.scale_by(img, self.scale_factor))
            self.animations["Walk"][direction] = frames

    def move(self, obstacles):
        if self.ispaused:
            return

        dx = dy = 0
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            dx = -self.speed
            self.direction = "left"
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
            self.direction = "right"
            moving = True
        elif keys[pygame.K_UP] or keys[pygame.K_z]:
            dy = -self.speed
            self.direction = "up"
            moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
            self.direction = "down"
            moving = True

        self.state = "Walk" if moving else "Idle"

        # --- COLLISION X ---
        self.rect.x += dx
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if dx > 0:
                    self.rect.right = obstacle.left
                elif dx < 0:
                    self.rect.left = obstacle.right
        # --- COLLISION Y ---
        self.rect.y += dy
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if dy > 0:
                    self.rect.bottom = obstacle.top
                elif dy < 0:
                    self.rect.top = obstacle.bottom
        # Synchronisation monde
        self.posix = self.rect.centerx
        self.posiy = self.rect.centery

        self.animate()

    def animate(self):
        """Fait défiler les images"""
        current_anim = self.animations[self.state][self.direction]

        # On augmente l'index
        self.frame_index += self.anim_speed

        # Si on dépasse le nombre d'images, on revient à 0
        if self.frame_index >= len(current_anim):
            self.frame_index = 0

        # On prend l'image (l'index devient un nombre entier : 0, 1, 2...)
        self.image = current_anim[int(self.frame_index)]

    def check_interaction(self, npcs):
        interaction_rect = self.get_interaction_rect()

        for npc in npcs:
            if interaction_rect.colliderect(npc.rect):
                return npc.name
        return None

    def lock(self):
        self.ispaused = True

    def unlock(self):
        self.ispaused = False

    def get_interaction_rect(self):
        taille_zone = 48
        distance_devant = 48
        
        rect = pygame.Rect(0, 0, taille_zone, taille_zone)
        rect.center = self.rect.center

        if self.direction == "up":
            rect.centery -= distance_devant
        elif self.direction == "down":
            rect.centery += distance_devant
        elif self.direction == "left":
            rect.centerx -= distance_devant
        elif self.direction == "right":
            rect.centerx += distance_devant
            
        return rect

    @property
    def visual_center_y(self):
        return self.rect.bottom - self.image.get_height() // 2

    def draw(self, screen, camera_x, camera_y):
        """Affiche le joueur à la bonne position sur l'écran"""
        player_rect_screen = self.rect.copy()
        player_rect_screen.x -= camera_x
        player_rect_screen.y -= camera_y
        
        # On aligne sur les pieds
        player_image_rect = self.image.get_rect(midbottom=player_rect_screen.midbottom)
        screen.blit(self.image, player_image_rect)