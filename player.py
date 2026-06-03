#Authert: Dvir Zilber

import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, player_id):
        super().__init__()
        self.image = pygame.Surface((40, 80), pygame.SRCALPHA)
        head_color = (200, 200, 200)
        pygame.draw.rect(self.image, head_color, (10, 0, 20, 20))
        pygame.draw.rect(self.image, color, (0, 20, 40, 60))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.id = player_id
        self.health = 6
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.on_ground = False
        self.double_jump = False

        #Track which way the player is facing (1 for right, -1 for left)
        self.facing = 1 if player_id == 1 else -1
        #Cooldown tracking (in milliseconds)
        self.last_shot_time = -1500  # Sets it to the past so they start ready to shoot
        self.cooldown = 1500  # 1.5 seconds

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_a]:
            self.vel_x = -self.speed
            self.facing = -1  #Look left
        if keys[pygame.K_d]:
            self.vel_x = self.speed
            self.facing = 1  # Look right

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -15
            self.on_ground = False
            self.double_jump = True
        if keys[pygame.K_SPACE] and self.double_jump and -5 < self.vel_y:
            self.vel_y = -15
            self.double_jump = False

    def update(self):
        if not self.on_ground:
            self.vel_y += 0.7
        else:
            if self.vel_y > 0:
                self.vel_y = 0

        self.rect.y += self.vel_y
        self.rect.x += self.vel_x

        if self.rect.bottom >= 500:
            self.rect.bottom = 500
            self.on_ground = True
            self.double_jump = False
        else:
            self.on_ground = False

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > 800: self.rect.right = 800