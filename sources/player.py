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
        self.anim_speed = 0.16

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
                        scaled_frame = pygame.transform.scale_by(
                            frame, self.scale_factor
                        )
                        frames.append(scaled_frame)
                    self.animations[state][direction] = frames

    def move(self, walls):
        if self.ispaused:
            return

        dx = dy = 0
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.direction = "left"
            moving = True
        elif keys[pygame.K_RIGHT]:
            dx = self.speed
            self.direction = "right"
            moving = True
        elif keys[pygame.K_UP]:
            dy = -self.speed
            self.direction = "up"
            moving = True
        elif keys[pygame.K_DOWN]:
            dy = self.speed
            self.direction = "down"
            moving = True

        self.state = "Walk" if moving else "Idle"

        # --- COLLISION X ---
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dx > 0:
                    self.rect.right = wall.rect.left
                elif dx < 0:
                    self.rect.left = wall.rect.right
        # --- COLLISION Y ---
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dy > 0:
                    self.rect.bottom = wall.rect.top
                elif dy < 0:
                    self.rect.top = wall.rect.bottom
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
        interaction_rect = self.rect.inflate(40, 40)

        for npc in npcs:
            if interaction_rect.colliderect(npc.rect):
                return npc.name
        return None

    def lock(self):
        self.ispaused = True

    def unlock(self):
        self.ispaused = False
