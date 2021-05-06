import pygame
import random
import math

from pygame.locals import*

blue = (0, 0, 255)
red = (220, 20, 60)
dark_red = (139, 0, 0)
light_blue = (173, 188, 230)
purple = (138, 43, 226)
white = (255, 255, 255)


class explosion_particles_class:
    def __init__(self, color, location):
        self.color = color
        self.location = location
        self.breadth = random.randint(20, 30)
        self.length = self.breadth
        self.rect = pygame.Rect(
            self.location[0], self.location[1], self.breadth, self.length)
        self.y_momentum = random.randint(-2, 2)
        self.x_momentum = random.randint(-1, 1)/5
        self.movement = [0, 0]

    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.color, [
                         self.rect[0], self.rect[1], self.length, self.breadth])

    def move(self, scroll):
        self.movement = [0, 0]
        self.movement[0] -= scroll[0]
        self.movement[0] += self.x_momentum
        self.movement[1] += self.y_momentum
        self.y_momentum += 0.05
        self.length -= 0.1
        self.breadth -= 0.1
        self.rect = pygame.Rect(
            self.rect[0], self.rect[1], self.breadth, self.length)

    def check_move(self, lava_rects, platform_rects):
        self.rect[0] += self.movement[0]

        self.rect[1] += self.movement[1]

        self.collision_test(lava_rects)

        for tile in self.tiles_hit:
            self.rect.bottom = tile.top
            self.y_momentum = random.randint(-2, 2)
            self.x_momentum = random.randint(-2, 2)

        self.collision_test(platform_rects)

        for tile in self.tiles_hit:
            self.rect.bottom = tile.top
            self.y_momentum = random.randint(-2, 2)
            self.x_momentum = random.randint(-2, 2)

    def collision_test(self, tile_rects):
        self.tiles_hit = []
        for tile in tile_rects:
            if tile.colliderect(self.rect):
                self.tiles_hit.append(tile)


class particle_class:
    def __init__(self, bullet, flag):
        if flag == 'player':
            self.color = blue
        else:
            self.color = red
        self.x = bullet.bullet_rect.center[0]
        self.y = bullet.bullet_rect.center[1]
        self.center = [self.x, self.y]
        self.radius = 5
        self.angle = bullet.angle
        self.dx = math.cos(self.angle)*1
        self.dy = math.sin(self.angle)*1

    def draw(self, SCREEN):
        pygame.draw.circle(SCREEN, self.color, [int(
            self.center[0]), int(self.center[1])], int(self.radius))

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.center[0] = int(self.x)
        self.center[1] = int(self.y)
        self.update()

    def update(self):
        self.radius -= 0.3


class lava_class:
    def __init__(self, offset):
        self.color = red
        self.radius = 0
        self.center = [1200-offset, 100]
        self.y_momentum = 0
        self.x_speed = random.choice([-0.05, 0, 0.05])
        self.rate = 0.1
        self.fall = True

    def draw(self, SCREEN):
        pygame.draw.circle(SCREEN, self.color, [int(
            self.center[0]), int(self.center[1])], int(self.radius))

    def move(self, scroll):
        self.center[0] -= scroll[0]
        self.center[1] += self.y_momentum
        self.y_momentum += 0.05
        self.center[0] += self.x_speed
        self.update()

    def update(self):
        self.radius += self.rate

    def check_move(self, rects, moving_rects):
        self.lava_rect = pygame.Rect(
            self.center[0]-self.radius, self.center[1]-self.radius, 2*self.radius, 2*self.radius)
        self.collision_test(rects)

        for tile in self.tiles_hit:
            self.lava_rect.bottom = tile.top
            self.center[0] = self.lava_rect[0]+self.radius
            self.center[1] = self.lava_rect[1]+self.radius
            self.rate = random.randint(-10, -5)/100
            self.y_momentum = random.randint(-2, 2)
            self.x_speed = random.randint(-2, 2)

        self.moving_collision_test(moving_rects)
        for tile in self.tiles_hit:
            self.lava_rect.bottom = tile.top
            self.center[0] = self.lava_rect[0]+self.radius
            self.center[1] = self.lava_rect[1]+self.radius
            self.rate = random.randint(-10, -5)/100
            self.y_momentum = random.randint(-2, 2)
            self.x_speed = random.randint(-2, 2)

    def collision_test(self, tile_rects):
        self.tiles_hit = []
        for tile in tile_rects:
            if tile.colliderect(self.lava_rect):
                self.tiles_hit.append(tile)

    def moving_collision_test(self, tile_rects):
        self.tiles_hit = []
        for tile in tile_rects:
            if tile.colliderect(self.lava_rect):
                self.tiles_hit.append(tile)


class player_health_bar:
    def __init__(self):
        self.color = purple
        self.dimension = [25, 25]
        self.list = [(100, 25), (125, 25), (150, 25), (175, 25), (200, 25), (225, 25), (250, 25), (275, 25), (300, 25), (325, 25),
                     (350, 25), (375, 25), (400, 25), (425, 25), (450, 25), (475, 25), (500, 25), (525, 25), (550, 25), (575, 25)]
        self.height = 25
        self.width = 500
        self.target_list = []
        self.hit = False

    def draw(self, SCREEN, player):
        if self.dimension[0] > 0:
            if self.hit and len(self.list) > 0:
                self.dimension[0] -= 1
                self.width -= 1
                if self.dimension[0] <= 0:
                    self.dimension[0] = 25
                    self.hit = False
                    del self.list[len(self.list)-1]

        if self.width > 0:
            pygame.draw.rect(SCREEN, self.color, [
                             100, 25, self.width, self.height])

    def update(self, player):
        if player.player_hit:
            self.hit = True


class enemy_health_bar:
    def __init__(self, enemy):
        self.color = red
        self.dimension = [40, 5]
        self.location = [enemy[0], enemy[1]-10]
        self.decrease = 0
        self.rate = 0.5

    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.color, [
                         self.location[0], self.location[1], self.dimension[0], self.dimension[1]])

    def update(self, enemy, SCREEN):
        self.location = [enemy[0], enemy[1]-10]
        if self.decrease > 0:
            self.dimension[0] -= self.rate
            self.decrease -= self.rate


class child_health_bar:
    def __init__(self):
        self.color = light_blue
        self.dimension = [25, 25]
        self.list = [(600, 25), (625, 25), (650, 25), (675, 25), (700, 25), (725, 25), (750, 25), (775, 25), (800, 25), (825, 25),
                     (850, 25), (875, 25), (900, 25), (925, 25), (950, 25), (975, 25), (1000, 25), (1025, 25), (1050, 25), (1075, 25)]
        self.height = 25
        self.width = 500
        self.target_list = []
        self.hit = False

    def draw(self, SCREEN, child):
        if self.dimension[0] > 0:
            if self.hit and len(self.list) > 0:
                self.dimension[0] -= 1
                self.width -= 1
                if self.dimension[0] <= 0:
                    self.dimension[0] = 25
                    self.hit = False
                    del self.list[len(self.list)-1]

        if self.width > 0:
            pygame.draw.rect(SCREEN, self.color, [
                             600, 25, self.width, self.height])

    def update(self, child):
        if child.child_hit:

            self.hit = True


class stick_timer:
    def __init__(self, player, child):
        self.color = light_blue
        self.combined_dimension = [30, 5]
        self.location = [child.child_rect[0], child.child_rect[1]-10]

    def draw(self, SCREEN, player, child):
        if self.combined_dimension[0] > 30:
            self.combined_dimension[0] = 30
        if player.stick == False:
            self.location[0] = child.child_rect[0]
            self.location[1] = child.child_rect[1]-10
        else:
            self.location[0] = player.player_rect[0]+5
            self.location[1] = player.player_rect[1]-10
        if self.combined_dimension[0] > 0:
            pygame.draw.rect(SCREEN, self.color, [
                             self.location[0], self.location[1], self.combined_dimension[0], self.combined_dimension[1]])
        if player.stick:
            self.combined_dimension[0] -= 0.08


class lava_timer_class:
    def __init__(self):
        self.color = light_blue
        self.dimension = [140, 10]
        self.location = [600, 150]
        self.rate = -0.3

    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.color, [
                         self.location[0], self.location[1], self.dimension[0], self.dimension[1]])

    def update(self, SCREEN, scroll):
        self.location[0] -= scroll[0]
        self.dimension[0] += self.rate
        self.draw(SCREEN)


class impact_particles_class:
    def __init__(self, bullet_loc, player_loc, color):
        self.color = color
        self.radius = random.randint(5, 10)
        self.speed = random.randint(1, 5)
        self.center = [player_loc[0], player_loc[1]]
        self.angle = random.uniform(math.atan2(bullet_loc[1]-player_loc[1], bullet_loc[0]-player_loc[0])-0.785, math.atan2(
            bullet_loc[1]-player_loc[1], bullet_loc[0]-player_loc[0])+0.785)
        self.dx = math.cos(self.angle)*self.speed
        self.dy = math.sin(self.angle)*self.speed

    def draw(self, SCREEN):
        pygame.draw.circle(SCREEN, self.color, [int(
            self.center[0]), int(self.center[1])], int(self.radius))

    def move(self, SCREEN):
        self.center[0] += self.dx
        self.center[1] += self.dy
        self.draw(SCREEN)

    def update(self):
        self.radius -= 0.1
        self.speed -= 0.5


class shockwave_class:
    def __init__(self, loc, color):
        self.color = color
        self.radius = 40
        self.width = 15
        self.center = loc

    def draw(self, SCREEN):
        pygame.draw.circle(SCREEN, self.color, [int(self.center[0]), int(
            self.center[1])], self.radius, int(self.width))

    def update(self, SCREEN):
        if self.width <= 5:
            self.radius += 100
        elif self.width >= 8:
            self.radius += 20

        else:
            self.radius += 2
        self.width -= 0.1
        self.draw(SCREEN)


class afterwave_class:
    def __init__(self, loc, color):
        self.color = color
        self.radius = 20
        self.width = 9
        self.center = [loc[0]+random.choice([random.randint(-20, -10), random.randint(
            10, 20)]), loc[1]+random.choice([random.randint(-20, -10), random.randint(10, 20)])]

    def draw(self, SCREEN):
        pygame.draw.circle(SCREEN, self.color, [int(self.center[0]), int(
            self.center[1])], self.radius, int(self.width))

    def update(self, SCREEN):
        if self.width <= 5:
            self.radius += 20
        elif self.width >= 8:
            self.radius += 10

        else:
            self.radius += 2
        self.width -= 0.1
        self.draw(SCREEN)
