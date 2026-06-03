#Authert: Dvir Zilber

import pygame


class Fireball:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 10
        self.radius = 8
        self.color = (255, 165, 0)

        # Create an invisible rectangular hit-box for collisions
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        self.x += self.speed * self.direction

        # Keep the invisible hit-box locked to the fireball's location
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)