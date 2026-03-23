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
        self.rect.midbottom = (x, y)
        self.draw_offset_y = -76

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

    def point_in_polygon(self, point, polygon):
        x, y = point
        inside = False
        j = len(polygon) - 1
        for i in range(len(polygon)):
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            if ((yi > y) != (yj > y)) and \
                (x < (xj - xi) * (y - yi) / (yj - yi + 0.00001) + xi):
                    inside = not inside
            j = i
        return inside

    def segments_intersect(self, p1, p2, p3, p4):
        def cross(o, a, b):
            return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
        d1 = cross(p3, p4, p1)
        d2 = cross(p3, p4, p2)
        d3 = cross(p1, p2, p3)
        d4 = cross(p1, p2, p4)
        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
        ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True
        return False

    def rect_polygon_collision(self, rect, polygon):
    # Cas 1 : un coin du rect est dans le polygone
        for p in [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]:
            if self.point_in_polygon(p, polygon):
                return True
    # Cas 2 : un sommet du polygone est dans le rect
        for p in polygon:
            if rect.collidepoint(p):
                return True
    # Cas 3 (manquant !) : une arête du polygone croise une arête du rect
        rect_edges = [
            (rect.topleft,     rect.topright),
            (rect.topright,    rect.bottomright),
            (rect.bottomright, rect.bottomleft),
            (rect.bottomleft,  rect.topleft),
            ]
        n = len(polygon)
        for i in range(n):
            arete_poly = (polygon[i], polygon[(i + 1) % n])
            for arete_rect in rect_edges:
                if self.segments_intersect(*arete_poly, *arete_rect):
                    return True
        return False
       
    
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
        for wall in obstacles:
            wall_rect = wall.rect if hasattr(wall, 'rect') else wall
            if not self.rect.colliderect(wall_rect):
                continue
            points = getattr(wall, 'points', None)
            if points:
                if self.rect_polygon_collision(self.rect, points):
                    self.rect.x -= dx  # ← annulation simple, pas de push
            else:
                if dx > 0: self.rect.right = wall_rect.left
                elif dx < 0: self.rect.left = wall_rect.right

# --- COLLISION Y ---
        self.rect.y += dy
        for wall in obstacles:
            wall_rect = wall.rect if hasattr(wall, 'rect') else wall
            if not self.rect.colliderect(wall_rect):
                continue
            points = getattr(wall, 'points', None)
            if points:
                if self.rect_polygon_collision(self.rect, points):
                    self.rect.y -= dy  # ← annulation simple, pas de push
            else:
                if dy > 0: self.rect.bottom = wall_rect.top
                elif dy < 0: self.rect.top = wall_rect.bottom

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
        player_rect_screen = self.rect.copy()
        player_rect_screen.x -= camera_x
        player_rect_screen.y -= camera_y

        player_image_rect = self.image.get_rect(
            midbottom=(player_rect_screen.centerx, player_rect_screen.bottom - self.draw_offset_y)
        )
        screen.blit(self.image, player_image_rect)
        pygame.draw.rect(screen, (0, 255, 0), player_rect_screen, 2)