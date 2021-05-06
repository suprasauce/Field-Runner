from pygame.locals import*
import pygame
import sys
import random
import math
import effects
import levels


pygame.init()


SCREEN_SIZE = (1200, 700)
SCREEN = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('FIELD RUNNER')
clock = pygame.time.Clock()
white = (255, 255, 255)
black = (0, 0, 0)
red = (220, 20, 60)
grey = (128, 128, 128)
purple = (138, 43, 226)
blue = (0, 0, 255)
light_blue = (173, 188, 230)
tor = (64, 224, 208)
aqua = (0, 255, 191)
light_purple = (147, 112, 219)
right = 3
left = -3


mouse = [0, 0]


bullet_particle = -4


pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.mixer.set_num_channels(16)


# ------------------------------------------------------------------------------------------------------------------------------------------------
class player_class:

    def __init__(self, combined):
        self.color = purple
        self.dimension = (40, 40)
        self.player_rect = pygame.Rect(
            SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2, self.dimension[0], self.dimension[1])
        self.moving_right = False
        self.moving_left = False
        self.player_movement = [0, 0]
        self.y_momentum = 0
        self.fall = True
        self.jump = False
        self.jump_count = 0
        self.stick = False
        self.x_momentum = 0
        self.shoot_right = False
        self.shoot_left = False
        self.player_hit = False
        self.combined = combined
        self.combined_dimension = (40, 70)
        self.combined_rect = self.combined.get_rect()
        self.player_c_child = False
        self.player_c_moving = False
        self.direction = 0
        self.shooting = False
        self.shock = False
        self.menu = False
        self.control = True

    def draw(self, SCREEN):
        if self.stick:
            SCREEN.blit(self.combined,
                        (self.combined_rect[0], self.combined_rect[1]))

        else:
            pygame.draw.rect(SCREEN, self.color, [
                             self.player_rect[0], self.player_rect[1], self.dimension[0], self.dimension[1]])

    def get_input(self, child, platform_rects, moving_platform_rects, enemies_rects, enemy_bullet_list, stick_power, bullet_list, impact_particles, shockwave_list, afterwave_list, total_wave, jump_sound, shoot_sound, hit_sound, wave_sound, stick_sound):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                shoot_sound.play()
                self.shooting = True
                mouse = pygame.mouse.get_pos()
                bullet_list.append(bullet_class(self.player_rect, mouse))
                if mouse[0]-self.player_rect[0] > 0:
                    self.x_momentum = -1
                    self.shoot_right = True
                    self.moving_left = True
                else:
                    self.x_momentum = 1
                    self.shoot_left = True
                    self.shoot_right = False
                    self.moving_right = True

            elif event.type == pygame.MOUSEBUTTONUP:
                self.shooting = False

            elif event.type == pygame.KEYDOWN and self.control:

                if event.key == pygame.K_m and total_wave > 0:
                    wave_sound.play()
                    shockwave_list.append(effects.shockwave_class(
                        [self.player_rect.center[0], self.player_rect.center[1]], self.color))
                    afterwave_list.append(effects.afterwave_class(
                        [self.player_rect.center[0], self.player_rect.center[1]], light_purple))
                    self.shock = True

                if event.key == pygame.K_ESCAPE:
                    self.menu = True

                if event.key == pygame.K_d:
                    self.moving_right = True

                if event.key == pygame.K_a:
                    self.moving_left = True

                if event.key == pygame.K_w and self.jump_count < 2:
                    jump_sound.play()
                    self.fall = False
                    self.y_momentum = -8
                    self.jump = True
                    self.jump_count += 1

                if event.key == pygame.K_SPACE and self.player_c_child == True:
                    stick_sound.play()
                    if stick_power.combined_dimension[0] > 0:
                        self.moving_right = False
                        self.moving_left = False
                        self.stick = True
                        self.combined_rect[0] = self.player_rect[0]
                        self.combined_rect[1] = self.player_rect[1]+30
                        self.player_rect = self.combined_rect

            elif event.type == pygame.KEYUP:

                if event.key == pygame.K_d:
                    self.moving_right = False

                if event.key == pygame.K_a:
                    self.moving_left = False

        self.movement(child, platform_rects, moving_platform_rects,
                      enemies_rects, enemy_bullet_list, impact_particles, hit_sound)

    def movement(self, child, platform_rects, moving_platform_rects, enemies_rects, enemy_bullet_list, impact_particles, hit_sound):
        self.player_movement = [0, 0]

        if self.player_c_moving:
            self.player_movement[0] += 1*self.direction

        if self.moving_left and self.x_momentum == 0:

            self.player_movement[0] += left

        if self.moving_right and self.x_momentum == 0:
            self.player_movement[0] += right

        for bullet in enemy_bullet_list:
            if bullet.bullet_rect.colliderect(self.player_rect):
                hit_sound.play()
                for i in range(10):
                    impact_particles.append(effects.impact_particles_class([bullet.x, bullet.y], [
                                            self.player_rect.center[0], self.player_rect.center[1]], self.color))
                self.player_hit = True
                enemy_bullet_list.remove(bullet)
                break
            else:
                self.player_hit = False

        if self.shoot_left:
            self.player_movement[0] += self.x_momentum
            self.x_momentum -= 0.1
            if self.x_momentum <= 0:
                self.moving_right = False
                self.x_momentum = 0
                self.shoot_left = False

        if self.shoot_right:
            self.player_movement[0] += self.x_momentum
            self.x_momentum += 0.1
            if self.x_momentum >= 0:
                self.moving_left = False
                self.x_momentum = 0
                self.shoot_right = False

        if self.fall:
            self.player_movement[1] += self.y_momentum
            self.y_momentum += 0.3

        if self.jump:
            self.player_movement[1] += self.y_momentum
            self.y_momentum += 0.3
            if self.y_momentum >= 0:
                self.fall = True
                self.jump = False

        self.check_move(child, platform_rects,
                        moving_platform_rects, enemies_rects)

    def collision_test(self, tile_rects):

        self.tiles_hit = []
        for tile in tile_rects:
            if self.player_rect.colliderect(tile):
                self.tiles_hit.append(tile)

    def collision_test_moving(self, tile_rects):

        self.tiles_hit = []
        for tile in tile_rects:
            if self.player_rect.colliderect(tile[0]):
                self.tiles_hit.append(tile[0])
                self.direction = tile[1]

    def check_move(self, child, platform_rects, moving_platform_rects, enemies_rects):
        self.player_rect.x += self.player_movement[0]

        self.collision_test(platform_rects)

        if self.stick == False:
            if self.player_rect.colliderect(child.child_rect):
                self.side = True
            else:
                self.side = False

        if self.moving_right:
            for tile in self.tiles_hit:
                self.player_rect.right = tile.left

        if self.moving_left:
            for tile in self.tiles_hit:
                self.player_rect.left = tile.right

        self.collision_test(enemies_rects)

        if self.moving_right:
            for tile in self.tiles_hit:
                self.player_rect.right = tile.left
                self.shoot_left = False
                self.moving_right = False
                self.x_momentum = 0

        if self.moving_left:
            for tile in self.tiles_hit:
                self.player_rect.left = tile.right
                self.moving_left = False
                self.shoot_right = False
                self.x_momentum = 0

        self.player_rect.y += self.player_movement[1]

        self.collision_test(platform_rects)

        if self.side == False and self.stick == False:
            if self.fall:
                if self.player_rect.colliderect(child.child_rect):
                    self.player_rect.bottom = child.child_rect.top
                    self.jump_count = 0
                    self.y_momentum = 0

            if self.jump:
                if self.player_rect.colliderect(child.child_rect):
                    self.player_rect.top = child.child_rect.bottom
                    self.y_momentum = 0

        if self.fall:

            for tile in self.tiles_hit:
                self.player_rect.bottom = tile.top
                self.player_c_moving = False
                self.jump_count = 0
                self.y_momentum = 0

        if self.jump:
            for tile in self.tiles_hit:
                self.player_rect.top = tile.bottom
                self.y_momentum = 0

        self.collision_test_moving(moving_platform_rects)

        if self.side == False and self.stick == False:
            if self.fall:
                if self.player_rect.colliderect(child.child_rect):
                    self.player_rect.bottom = child.child_rect.top
                    self.jump_count = 0
                    self.y_momentum = 0
            if self.jump:
                if self.player_rect.colliderect(child.child_rect):
                    self.player_rect.top = child.child_rect.bottom
                    self.y_momentum = 0

        if self.fall:

            for tile in self.tiles_hit:
                self.player_rect.bottom = tile.top
                self.player_c_moving = True
                self.jump_count = 0
                self.y_momentum = 0

        if self.moving_right or self.moving_left:
            self.player_c_moving = False

        if self.jump:
            for tile in self.tiles_hit:
                self.player_rect.top = tile.bottom
                self.y_momentum = 0

        self.collision_test(enemies_rects)

        if self.fall:

            for tile in self.tiles_hit:
                self.player_rect.bottom = tile.top

                self.jump_count = 0
                self.y_momentum = 0

        if self.jump:
            for tile in self.tiles_hit:
                self.player_rect.top = tile.bottom
                self.y_momentum = 0


# ------------------------------------------------------------------------------------------------------------------------------------------------
class child_class:
    def __init__(self):
        self.color = light_blue
        self.dimension = [30, 30]
        self.child_rect = pygame.Rect(
            100, 400, self.dimension[0], self.dimension[1])
        self.fall = True
        self.y_momentum = -15
        self.child_movement = [0, 0]
        self.side_hit = 'none'
        self.moving_right = False
        self.moving_left = False
        self.x_momentum = 0
        self.hit_right = False
        self.hit_left = False
        self.child_c_moving = False
        self.direction = 0
        self.child_hit = False
        self.start = 0
        self.letter = True
        self.rate = 10
        self.child_hit = False

    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.color, [self.child_rect.x, self.child_rect.y, int(
            self.dimension[0]), int(self.dimension[1])])

    def movement(self, player, platform_rects, enemies_rects, enemy, bullet_list, enemy_bullet_list, moving_platform_rects, impact_particles, hit_sound):
        self.child_movement = [0, 0]

        for bullet in enemy_bullet_list:
            if bullet.bullet_rect.colliderect(self.child_rect):
                for i in range(10):
                    impact_particles.append(effects.impact_particles_class([bullet.x, bullet.y], [
                                            self.child_rect.center[0], self.child_rect.center[1]], self.color))
                self.child_hit = True
                enemy_bullet_list.remove(bullet)
                break
            else:
                self.child_hit = False

        if self.letter:
            self.child_movement[0] += self.rate
            self.rate -= 0.1

        if self.letter:
            self.start += 1
            if self.start >= 90:
                self.letter = False

        if self.child_c_moving:
            self.child_movement[0] += self.direction

        if player.player_rect.colliderect(self.child_rect):
            if player.player_movement[0] > 0:
                self.side_hit = 'right'
            elif player.player_movement[0] < 0:
                self.side_hit = 'left'
        else:
            self.side_hit = 'none'
            self.moving_right = False
            self.moving_left = False

        if self.side_hit != 'none':
            player.player_c_child = True

        else:
            player.player_c_child = False

        if self.side_hit == 'right':
            self.child_rect.left = player.player_rect.right
            self.moving_right = True
        elif self.side_hit == 'left':
            self.child_rect.right = player.player_rect.left
            self.moving_left = True

        for bullet in bullet_list:

            if bullet.bullet_rect.colliderect(self.child_rect):
                hit_sound.play()
                for i in range(10):
                    impact_particles.append(effects.impact_particles_class([bullet.x, bullet.y], [
                                            self.child_rect.center[0], self.child_rect.center[1]], self.color))
                self.child_hit = True
                if bullet.bullet_movement[0] > 0:

                    self.x_momentum = 2
                    self.hit_left = True

                elif bullet.bullet_movement[0] < 0:

                    self.x_momentum = -3
                    self.hit_right = True

                bullet_list.remove(bullet)
                break

            else:
                self.child_hit = False

        for bullet in enemy_bullet_list:
            if bullet.bullet_rect.colliderect(self.child_rect):
                hit_sound.play()
                if bullet.enemy_bullet_movement[0] > 0:

                    self.x_momentum = 2
                    self.hit_left = True

                elif bullet.enemy_bullet_movement[0] < 0:

                    self.x_momentum = -2
                    self.hit_right = True

                enemy_bullet_list.remove(bullet)
                break

        self.child_movement[0] += self.x_momentum

        if self.hit_right:
            self.x_momentum += 0.3
            if self.x_momentum >= 0:
                self.x_momentum = 0
                self.hit_right = False

        elif self.hit_left:
            self.x_momentum -= 0.3
            if self.x_momentum <= 0:
                self.x_momentum = 0
                self.hit_left = False

        if self.fall:
            self.child_movement[1] += self.y_momentum
            self.y_momentum += 0.5

        self.check_move(player, platform_rects,
                        enemies_rects, moving_platform_rects)

    def check_move(self, player, platform_rects, enemies_rects, moving_platform_rects):
        self.child_rect[0] += self.child_movement[0]

        self.collision_test(platform_rects)

        for tile in self.tiles_hit:
            self.child_rect[0] = self.child_rect[0]-self.child_movement[0]
            self.x_momentum = 0
            break

        if self.moving_right:
            for tile in self.tiles_hit:
                self.child_rect.right = tile.left
                player.player_rect.right = self.child_rect.left

        if self.moving_left:
            for tile in self.tiles_hit:
                self.child_rect.left = tile.right
                player.player_rect.left = self.child_rect.right

        self.collision_test(enemies_rects)

        for tile in self.tiles_hit:

            if self.hit_left:
                self.child_rect.right = tile.left
            elif self.hit_right:
                self.child_rect.left = tile.right
            self.x_momentum = 0
            break

        if self.moving_right:
            for tile in self.tiles_hit:
                self.child_rect.right = tile.left
                player.player_rect.right = self.child_rect.left
                self.moving_left = False

        if self.moving_left:
            for tile in self.tiles_hit:
                self.child_rect.left = tile.right
                player.player_rect.left = self.child_rect.right
                self.moving_right = False

        self.child_rect[1] += int(self.child_movement[1])

        self.collision_test(platform_rects)

        if self.child_rect.colliderect(player.player_rect):
            if player.side == False:
                self.child_rect.bottom = player.player_rect.top
                self.y_momentum = 0

        if self.fall:
            for tile in self.tiles_hit:
                self.child_rect.bottom = tile.top
                self.y_momentum = 0
                self.child_c_moving = False

        self.moving_collision_test(moving_platform_rects)

        if self.child_rect.colliderect(player.player_rect):
            if player.side == False:
                self.child_rect.bottom = player.player_rect.top
                self.y_momentum = 0

        if self.fall:
            for tile in self.tiles_hit:
                self.child_rect.bottom = tile.top
                self.y_momentum = 0
                self.child_c_moving = True

        self.collision_test(enemies_rects)

        if self.fall:
            for tile in self.tiles_hit:
                self.child_rect.bottom = tile.top
                self.y_momentum = 0

    def collision_test(self, tile_rects):
        self.tiles_hit = []
        for tile in tile_rects:
            if self.child_rect.colliderect(tile):
                self.tiles_hit.append(tile)

    def moving_collision_test(self, tile_rects):
        self.tiles_hit = []
        for tile in tile_rects:
            if self.child_rect.colliderect(tile[0]):
                self.tiles_hit.append(tile[0])
                self.direction = tile[1]


# ------------------------------------------------------------------------------------------------------------------------------------------------
class enemy_class():
    def __init__(self, player, offset):
        self.color = red
        self.dimension = (40, 40)
        if offset == 0:
            self.enemy_rect = pygame.Rect(random.randint(
                player.player_rect[0]+140, SCREEN_SIZE[0]), -40, self.dimension[0], self.dimension[1])
        else:
            self.enemy_rect = random.choice([pygame.Rect(random.randint(0, player.player_rect[0]-100), -40, self.dimension[0], self.dimension[1]), pygame.Rect(
                random.randint(player.player_rect[0]+140, SCREEN_SIZE[0]), -40, self.dimension[0], self.dimension[1])])
        self.fall = True
        self.hit_right = False
        self.hit_left = False
        self.y_momentum = 0
        self.x_momentum = 0
        self.moving_right = False
        self.moving_left = False
        self.enemy_c_moving = False
        self.direction = 0
        self.shoot_right = False
        self.shoot_left = False
        self.enemy_health = effects.enemy_health_bar(self.enemy_rect)
        self.time = 1

    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.color, [self.enemy_rect.x, self.enemy_rect.y, int(
            self.dimension[0]), int(self.dimension[1])])
        self.enemy_health.update(self.enemy_rect, SCREEN)

    def movement(self, platform_rects, enemies_rects, bullet_list, player, child, stick_power, moving_platform_rects, enemy_list, impact_particles, total_score, hit_sound):
        self.enemy_movement = [0, 0]
        self.time += 1

        if self.time > 500:
            self.time = 1

        if self.time % 100 == 0 and abs(player.player_rect[0]-self.enemy_rect[0]) < 200:
            if self.enemy_rect[0]-player.player_rect[0] > 0:
                self.hit_left = True
                self.moving_right = True
                self.x_momentum = 4

            elif self.enemy_rect[0]-player.player_rect[0] < 0:
                self.hit_right = True
                self.moving_left = True
                self.x_momentum = -4

        if self.enemy_c_moving:
            self.enemy_movement[0] += self.direction

        for bullet in bullet_list:
            for enemy in enemy_list:
                if bullet.bullet_rect.colliderect(self.enemy_rect):
                    hit_sound.play()
                    total_score += 1
                    for i in range(10):
                        impact_particles.append(effects.impact_particles_class([bullet.x, bullet.y], [
                                                self.enemy_rect.center[0], self.enemy_rect.center[1]], self.color))
                    stick_power.combined_dimension[0] += 10
                    self.enemy_health.decrease = 10
                    if self.enemy_rect.center[0]-player.player_rect.center[0] > 0:

                        self.x_momentum = 3
                        self.hit_left = True
                        self.moving_right = True
                    else:

                        self.x_momentum = -3
                        self.hit_right = True
                        self.moving_left = True

                    bullet_list.remove(bullet)
                    break

        self.enemy_movement[0] += self.x_momentum
        if self.hit_right:
            self.x_momentum += 0.3
            if self.x_momentum >= 0:
                self.x_momentum = 0
                self.hit_right = False
                self.moving_left = False
        elif self.hit_left:
            self.x_momentum -= 0.3
            if self.x_momentum <= 0:
                self.x_momentum = 0
                self.hit_left = False
                self.moving_right = False

        if self.fall:
            self.enemy_movement[1] += self.y_momentum
            self.y_momentum += 0.3

        self.check_move(platform_rects, enemies_rects,
                        bullet_list, child, player, moving_platform_rects)

    def check_move(self, platform_rects, enemies_rects, bullet_list, child, player, moving_platform_rects):
        self.enemy_rect.x += self.enemy_movement[0]

        self.collision_test(platform_rects)

        for tile in self.tiles_hit:
            if self.enemy_movement[0] > 0:
                self.enemy_rect.right = tile.left
            else:
                self.enemy_rect.left = tile.right
            break

        self.tiles_hit = []

        if self.enemy_rect.colliderect(child.child_rect):
            self.tiles_hit.append(child.child_rect)

        if self.moving_right:
            for tile in self.tiles_hit:
                self.enemy_rect.right = tile.left

        if self.moving_left:
            for tile in self.tiles_hit:
                self.enemy_rect.left = tile.right

        self.collision_test(enemies_rects)

        if self.moving_right:
            for tile in self.tiles_hit:
                self.enemy_rect.right = tile.left

                self.x_momentum = 0

        if self.moving_left:
            for tile in self.tiles_hit:
                self.enemy_rect.left = tile.right

                self.x_momentum = 0

        self.enemy_rect.y += self.enemy_movement[1]

        self.collision_test(platform_rects)

        if self.fall:
            for tile in self.tiles_hit:
                self.enemy_rect.bottom = tile.top
                self.y_momentum = 0
                self.enemy_c_moving = False

        self.collision_test(enemies_rects)

        if self.fall:
            for tile in self.tiles_hit:
                self.enemy_rect.bottom = tile.top
                self.y_momentum = 0

        self.moving_collision_test(moving_platform_rects)

        if self.fall:
            for tile in self.tiles_hit:
                self.enemy_rect.bottom = tile.top
                self.enemy_c_moving = True
                self.y_momentum = 0

        self.collision_test(enemies_rects)

        if self.fall:
            for tile in self.tiles_hit:
                self.enemy_rect.bottom = tile.top
                self.y_momentum = 0
                self.enemy_c_moving = True

    def collision_test(self, tile_rects):
        self.tiles_hit = []
        for tile in tile_rects:
            if self.enemy_rect.colliderect(tile):
                self.tiles_hit.append(tile)

    def moving_collision_test(self, tile_rects):
        self.tiles_hit = []
        for tile in tile_rects:
            if self.enemy_rect.colliderect(tile[0]):
                self.tiles_hit.append(tile[0])
                self.direction = tile[1]


# ------------------------------------------------------------------------------------------------------------------------------------------------
class bullet_class:
    def __init__(self, player_rect, mouse):
        self.color = blue
        self.bullet_speed = 8
        self.radius = 1
        self.x = player_rect.center[0]
        self.y = player_rect.center[1]
        self.bullet_rect = pygame.Rect(self.x, self.y, 10, 10)
        self.angle = math.atan2(mouse[1]-player_rect.y, mouse[0]-player_rect.x)
        self.dx = math.cos(self.angle)*self.bullet_speed
        self.dy = math.sin(self.angle)*self.bullet_speed
        self.status = 'not_collided'
        self.bullet_movement = [0, 0]

    def draw(self, SCREEN):
        pygame.draw.circle(SCREEN, self.color, [
                           self.bullet_rect[0], self.bullet_rect[1]], int(self.radius))

    def move(self):
        self.bullet_movement = [0, 0]
        self.x += self.dx
        self.y += self.dy
        self.bullet_movement[0] += self.dx
        self.bullet_movement[1] += self.dy
        self.bullet_rect[0] = self.x
        self.bullet_rect[1] = self.y-15

    def check_move(self, platform_rects):
        self.collision_test(platform_rects)

    def collision_test(self, tile_rects):
        self.status = 'not_collided'
        for tile in tile_rects:
            if tile.colliderect(self.bullet_rect):
                self.status = 'collided'
                break


# ------------------------------------------------------------------------------------------------------------------------------------------------
class enemy_bullet_class:
    def __init__(self, enemy, player, child):
        self.color = red
        self.bullet_speed = 7
        self.radius = 1
        self.x = enemy.enemy_rect.center[0]
        self.y = enemy.enemy_rect.center[1]
        self.bullet_rect = pygame.Rect(self.x, self.y, 10, 10)
        self.angle = math.atan2(
            player.player_rect.y-enemy.enemy_rect.y, player.player_rect.x-enemy.enemy_rect.x)
        self.dx = math.cos(self.angle)*self.bullet_speed
        self.dy = math.sin(self.angle)*self.bullet_speed
        self.status = 'not_collided'
        self.enemy_bullet_movement = [0, 0]

    def draw(self, SCREEN):
        pygame.draw.circle(SCREEN, self.color, [int(
            self.x), int(self.y)], int(self.radius))

    def move(self):
        self.enemy_bullet_movement = [0, 0]
        self.x += self.dx
        self.y += self.dy
        self.enemy_bullet_movement[0] += self.dx
        self.enemy_bullet_movement[1] += self.dy
        self.bullet_rect[0] = int(self.x)
        self.bullet_rect[1] = int(self.y)

    def check_move(self, platform_rects):
        self.collision_test(platform_rects)

    def collision_test(self, tile_rects):
        self.status = 'not_collided'
        for tile in tile_rects:
            if tile.colliderect(self.bullet_rect):
                self.status = 'collided'
                break

# ------------------------------------------------------------------------------------------------------------------------------------------------


class gun_class:
    def __init__(self, player, glock1, glock2):
        self.dimension = (20, 10)
        self.angle = (180/math.pi)*-math.atan2(pygame.mouse.get_pos()
                                               [1]-player.player_rect.center[1], pygame.mouse.get_pos()[0]-player.player_rect.center[0])
        if self.angle <= 90 and self.angle >= -90:
            self.org_glock = glock1
        else:
            self.org_glock = glock2

        self.glock_rect = self.org_glock.get_rect()

    def draw(self, SCREEN, player):
        SCREEN.blit(self.glock, self.glock_rect)

    def update(self, SCREEN, player, glock1, glock2):
        self.angle = (180/math.pi)*-math.atan2(pygame.mouse.get_pos()
                                               [1]-player.player_rect.center[1], pygame.mouse.get_pos()[0]-player.player_rect.center[0])
        if self.angle <= 90 and self.angle >= -90:
            self.org_glock = glock1
        else:
            self.org_glock = glock2
        self.glock = pygame.transform.rotozoom(
            self.org_glock, int(self.angle), 1)
        self.glock_rect.center = player.player_rect.center
        self.draw(SCREEN, player)
# ------------------------------------------------------------------------------------------------------------------------------------------------


class enemy_gun_class:
    def __init__(self, enemy, player, glock1, glock2):
        self.color = white
        self.dimension = (20, 10)
        self.angle = (180/math.pi)*-math.atan2(
            player.player_rect.center[1]-enemy.enemy_rect.center[1], player.player_rect.center[0]-enemy.enemy_rect.center[0])
        if self.angle <= 90 and self.angle >= -90:
            self.org_glock = glock1
        else:
            self.org_glock = glock2

        self.glock_rect = self.org_glock.get_rect()

    def draw(self, SCREEN, enemy):
        SCREEN.blit(self.glock, self.glock_rect)

    def update(self, SCREEN, enemy, player, glock1, glock2):
        self.angle = (180/math.pi)*-math.atan2(
            player.player_rect.center[1]-enemy.enemy_rect.center[1], player.player_rect.center[0]-enemy.enemy_rect.center[0])
        if self.angle <= 90 and self.angle >= -90:
            self.org_glock = glock1
        else:
            self.org_glock = glock2
        self.glock = pygame.transform.rotozoom(
            self.org_glock, int(self.angle), 1)
        self.glock_rect.center = enemy.enemy_rect.center
        self.draw(SCREEN, enemy)


# ------------------------------------------------------------------------------------------------------------------------------------------------
def check(platform, rects):
    for rect in rects:
        if platform.colliderect(rect):
            return 'collided'

# ------------------------------------------------------------------------------------------------------------------------------------------------


def main():
    display = True
    display_childupdate = True
    offset = 0
    time = 1
    scroll = [0, 0]
    enemy_bullet_list = []
    bullet_list = []
    tiles_hit = []
    enemy_list = []
    particle_list = []
    lava_particles = []
    impact_particles = []
    shockwave_list = []
    afterwave_list = []
    jump_sound = pygame.mixer.Sound('data/jump.wav')
    shoot_sound = pygame.mixer.Sound('data/shoot.wav')
    explosion_sound = pygame.mixer.Sound('data/explosion.wav')
    hit_sound = pygame.mixer.Sound('data/hit.wav')
    wave_sound = pygame.mixer.Sound('data/wave_sound.wav')
    stick_sound = pygame.mixer.Sound('data/stick.wav')
    no_stick_sound = pygame.mixer.Sound('data/no_stick.wav')
    wave_timer_sound = pygame.mixer.Sound('data/wave_timer.wav')
    glock1 = pygame.image.load('data/glock1.png').convert_alpha()
    glock2 = pygame.image.load('data/glock2.png').convert_alpha()
    combined = pygame.image.load('data/combined.png').convert()
    letter_box1 = pygame.image.load('data/letter_box1.png').convert()
    letter_box2 = pygame.image.load('data/letter_box2.png').convert()
    glock1 = pygame.transform.scale(glock1, (40, 40))
    glock2 = pygame.transform.scale(glock2, (40, 40))
    letter_box1 = pygame.transform.scale(letter_box1, (60, 60))
    letter_box2 = pygame.transform.scale(letter_box2, (60, 60))
    letter_box_rect1 = letter_box1.get_rect()
    letter_box_rect2 = letter_box2.get_rect()
    letter_box_rect1[0] = 100
    letter_box_rect2[0] = 4700
    combined.set_colorkey(white)
    moving_platform_rects = []
    child = child_class()
    player = player_class(combined)
    player_bar = effects.player_health_bar()
    child_bar = effects.child_health_bar()
    lava_timer = effects.lava_timer_class()
    gun = gun_class(player, glock1, glock2)
    stick_power = effects.stick_timer(player, child)
    explosion_particles = []
    text_1 = pygame.font.Font(
        "data/impact.ttf", 30).render('SHOOT HERE', True, white)
    text_2 = pygame.font.Font(
        "data/impact.ttf", 30).render('SHOOT HERE', True, grey)
    text_1_rect = text_1.get_rect()
    text_1_rect[0] = 600
    text_1_rect[1] = 100
    text_2_rect = text_2.get_rect()
    text_2_rect[0] = 600
    text_2_rect[1] = 100
    platform_time = -300
    shoot_timer = False
    text1 = True
    text2 = False
    shockwave_time = 0
    fade_surf = pygame.Surface(SCREEN_SIZE)
    fade_surf.fill(black)
    alpha = 0
    play = True
    p_lava_hit = False
    c_lava_hit = False
    letter_box_combined = False
    shock_wave_timer = 0
    child_play = True
    player_play = True

    total_score = 0
    total_wave = 1

    score = pygame.font.Font(
        "data/impact.ttf", 30).render('SCORE :'+str(total_score), True, white)
    wave = pygame.font.Font(
        "data/impact.ttf", 30).render('SHOCK_WAVES :'+str(total_wave), True, white)

    while play:

        scroll[0] += player.player_rect.center[0]-scroll[0]-620

        offset += scroll[0]

        if len(enemy_list) < 3:
            enemy_list.append(enemy_class(player, offset))

        player.player_rect[0] -= scroll[0]
        child.child_rect[0] -= scroll[0]

        platform_rects = []
        lava_rects = []
        enemies_rects = []
        moving_platform_rects = []

        letter_box_rect1[0] -= scroll[0]
        letter_box_rect1[1] = 440

        letter_box_rect2[0] -= scroll[0]
        letter_box_rect2[1] = 440

        if player.stick and abs(player.player_rect[0]-letter_box_rect2[0]) == 40:
            letter_box_combined = True

        if abs(child.child_rect[0]-letter_box_rect2[0]) == 30:
            letter_box_combined = True

        platform_rects.append(letter_box_rect1)
        platform_rects.append(letter_box_rect2)

        text_2_rect[0] -= scroll[0]
        text_1_rect[0] -= scroll[0]

        SCREEN.fill(black)

        for platform in levels.platforms:
            platform[0] -= scroll[0]
            pygame.draw.rect(SCREEN, white, platform)
            platform_rects.append(pygame.Rect(platform))
        for lava in levels.lava:
            lava[0] -= scroll[0]
            pygame.draw.rect(SCREEN, red, lava)
            lava_rects.append(pygame.Rect(lava))

        for platform in levels.moving_platforms:
            platform[0] -= scroll[0]
            platform[0] += platform[4]
            if check(pygame.Rect([platform[0], platform[1], platform[2], platform[3]]), platform_rects) == 'collided':
                platform[4] = -platform[4]

            pygame.draw.rect(
                SCREEN, white, [platform[0], platform[1], platform[2], platform[3]])
            moving_platform_rects.append(
                [pygame.Rect([platform[0], platform[1], platform[2], platform[3]]), platform[4]])

        for enemy in enemy_list:
            if enemy.time % 100 == 0 and abs(player.player_rect[0]-enemy.enemy_rect[0]) < 250:
                shoot_sound.play()
                enemy_bullet_list.append(
                    enemy_bullet_class(enemy, player, child))
            enemy_gun = enemy_gun_class(enemy, player, glock1, glock2)
            enemy.enemy_rect[0] -= scroll[0]
            enemy.draw(SCREEN)

            enemy_gun.update(SCREEN, enemy, player, glock1, glock2)
            enemy.movement(platform_rects, enemies_rects, bullet_list, player, child, stick_power,
                           moving_platform_rects, enemy_list, impact_particles, total_score, hit_sound)

            if player.shock:
                total_score += 1
                explosion_sound.play()

                for i in range(10):
                    explosion_particles.append(effects.explosion_particles_class(
                        enemy.color, [enemy.enemy_rect.center[0], enemy.enemy_rect.center[1]]))
                enemy_list.remove(enemy)
                shockwave_time += 1

            if enemy.enemy_health.dimension[0] <= 0:
                explosion_sound.play()
                total_score += 1
                for i in range(10):
                    explosion_particles.append(effects.explosion_particles_class(
                        enemy.color, [enemy.enemy_rect.center[0], enemy.enemy_rect.center[1]]))
                enemy_list.remove(enemy)
                continue

            if enemy.enemy_rect.center[0] < -20 or enemy.enemy_rect.center[0] > 1240:
                enemy_list.remove(enemy)
                continue

            for rect in lava_rects:
                if enemy.enemy_rect.colliderect(rect):
                    explosion_sound.play()
                    for i in range(10):
                        explosion_particles.append(effects.explosion_particles_class(
                            enemy.color, [enemy.enemy_rect.center[0], enemy.enemy_rect.center[1]]))
                    enemy_list.remove(enemy)
                    break

            for lava in lava_particles:
                if lava.radius > 10:
                    if enemy.enemy_rect.colliderect(lava.lava_rect):
                        explosion_sound.play()
                        for i in range(10):
                            explosion_particles.append(effects.explosion_particles_class(
                                enemy.color, [enemy.enemy_rect.center[0], enemy.enemy_rect.center[1]]))
                        enemy_list.remove(enemy)
                        break

            enemies_rects.append(enemy.enemy_rect)

        for particle in particle_list:
            particle.draw(SCREEN)
            particle.move()
            if particle.radius <= 0:
                particle_list.remove(particle)

        player.get_input(child, platform_rects, moving_platform_rects, enemies_rects, enemy_bullet_list, stick_power, bullet_list,
                         impact_particles, shockwave_list, afterwave_list, total_wave, jump_sound, shoot_sound, hit_sound, wave_sound, stick_sound)

        if player.stick == False:
            child.movement(player, platform_rects, enemies_rects, enemy, bullet_list,
                           enemy_bullet_list, moving_platform_rects, impact_particles, hit_sound)
            if display_childupdate:
                child.draw(SCREEN)
        if display:
            player.draw(SCREEN)

        for bullet in bullet_list:

            particle_list.append(effects.particle_class(bullet, 'player'))
            bullet.move()

            if bullet.bullet_rect.colliderect(text_1_rect):
                bullet_list.remove(bullet)
                shoot_timer = True
                text1 = False
                text2 = True
                continue

            if bullet.bullet_rect[0] < 0 or bullet.bullet_rect[0] > 1200:
                bullet_list.remove(bullet)
                continue

            if bullet.bullet_rect[1] < 0 or bullet.bullet_rect[1] > 700:
                bullet_list.remove(bullet)
                continue

            bullet.check_move(platform_rects)
            if bullet.status == 'collided':

                bullet_list.remove(bullet)
            if bullet.bullet_rect.center[0] < -20 or bullet.bullet_rect.center[1] > 1240:
                bullet_list.remove(bullet)

        for bullet in enemy_bullet_list:

            particle_list.append(effects.particle_class(bullet, 'enemy'))
            bullet.move()

            bullet.check_move(platform_rects)
            if bullet.status == 'collided':
                enemy_bullet_list.remove(bullet)
                continue
            if bullet.bullet_rect.center[0] < -20 or bullet.bullet_rect.center[1] > 1240:
                enemy_bullet_list.remove(bullet)

        if shoot_timer == False and offset < 1000:
            if offset > 20:
                lava_particles.append(effects.lava_class(offset))

        for lava in lava_particles:
            lava.move(scroll)
            lava.check_move(lava_rects, platform_rects)
            lava.draw(SCREEN)
            if lava.center[1] > 1000 or lava.radius <= 0:
                lava_particles.remove(lava)

        for lava in lava_particles:
            if lava.radius > 10:
                if player.player_rect.colliderect(lava.lava_rect):
                    if player_play:
                        explosion_sound.play()
                        player_play = False
                    p_lava_hit = True
                    display = False
                    break

        for lava in lava_particles:
            if lava.radius > 10:
                if child.child_rect.colliderect(lava.lava_rect):
                    if child_play:
                        explosion_sound.play()
                        child_play = False
                    c_lava_hit = True
                    display_childupdate = False
                    break

        if display:
            gun.update(SCREEN, player, glock1, glock2)

        for tile in lava_rects:
            if player.player_rect.colliderect(tile):
                if player_play:
                    explosion_sound.play()
                    player_play = False
                player.player_rect.bottom = tile.top
                player.y_momentum = 0
                display = False
                p_lava_hit = True
                break

        for tile in lava_rects:
            if child.child_rect.colliderect(tile):
                if child_play:
                    explosion_sound.play()
                    child_play = False
                child.child_rect.bottom = tile.top
                child.y_momentum = 0
                display_childupdate = False
                c_lava_hit = True
                break

        if len(player_bar.list) == 0 or len(child_bar.list) == 0 or p_lava_hit == True or c_lava_hit:
            if len(player_bar.list) == 0:
                if player_play:

                    explosion_sound.play()
                    player_play = False
                display = False
            if len(child_bar.list) == 0:
                display_childupdate = False
                if child_play:
                    explosion_sound.play()
                    child_play = False
            pygame.time.delay(20)
            player.control = False

            if len(player_bar.list) == 0 or p_lava_hit:
                explosion_particles.append(effects.explosion_particles_class(
                    player.color, [player.player_rect.center[0], player.player_rect.center[1]]))
            if len(child_bar.list) == 0 or c_lava_hit:
                explosion_particles.append(effects.explosion_particles_class(
                    child.color, [child.child_rect.center[0], child.child_rect.center[1]]))

        if display:
            player_bar.update(player)
            player_bar.draw(SCREEN, player)

        player.player_hit = False
        if display_childupdate:

            child_bar.update(child)
            child_bar.draw(SCREEN, child)

        child.child_hit = False

        time += 1
        if time > 500:
            time = 1

        if shockwave_time > 2:
            player.shock = False
            shockwave_time = 0

        if stick_power.combined_dimension[0] < 0:
            no_stick_sound.play()
            stick_power.combined_dimension[0] = 0
            player.stick = False
            player.player_rect = pygame.Rect(
                player.combined_rect[0], player.combined_rect[1]+30, player.dimension[0], player.dimension[1])
            child.child_rect = pygame.Rect(
                player.player_rect[0]+5, player.player_rect[1]-40, child.dimension[0], child.dimension[1])
            child.y_momentum = -5

        if display_childupdate:
            stick_power.draw(SCREEN, player, child)

        for particle in explosion_particles:
            particle.move(scroll)
            particle.check_move(lava_rects, platform_rects)
            particle.draw(SCREEN)
            if particle.length <= 0 or particle.breadth <= 0:
                explosion_particles.remove(particle)

        for particle in impact_particles:
            particle.move(SCREEN)
            particle.update()
            if particle.radius <= 0:
                impact_particles.remove(particle)

        for enemy in enemy_list:
            enemy.enemy_health.draw(SCREEN)

        if text1:
            SCREEN.blit(text_1, text_1_rect)
        elif text2:
            SCREEN.blit(text_2, text_2_rect)

        if shoot_timer == False:
            lava_timer.location[0] -= scroll[0]

        if shoot_timer:
            lava_timer.update(SCREEN, scroll)
            if lava_timer.dimension[0] <= 0:
                shoot_timer = False
                lava_timer.dimension[0] = 140
                text1 = True
                text2 = False

        for circle in shockwave_list:
            if circle.width <= 2:
                shockwave_list.remove(circle)
            circle.update(SCREEN)

        for circle in afterwave_list:
            if circle.width <= 2:
                afterwave_list.remove(circle)
            circle.update(SCREEN)
        platform_time += 1
        if platform_time > 300:
            platform_time = -300

        SCREEN.blit(letter_box1, letter_box_rect1)
        SCREEN.blit(letter_box2, letter_box_rect2)

        if child.letter:

            pygame.time.delay(10)

        if player.player_rect[1] > 700:
            display = False

        if child.child_rect[1] > 700:
            display_childupdate = False

        SCREEN.blit(score, (100, 100))
        score = pygame.font.Font(
            "data/impact.ttf", 20).render('SCORE :'+str(total_score), True, white)
        SCREEN.blit(wave, (100, 150))
        wave = pygame.font.Font(
            "data/impact.ttf", 20).render('SHOCK_WAVE :'+str(total_wave), True, white)

        if display == False or display_childupdate == False:
            fade_surf.set_alpha(alpha)
            SCREEN.blit(fade_surf, (0, 0))
            alpha += 2

        if letter_box_combined:
            fade_surf.set_alpha(alpha)
            SCREEN.blit(fade_surf, (0, 0))
            alpha += 2

        if alpha == 300:
            player.menu = True

        if player.menu:
            play = False
            for platform in levels.platforms:
                platform[0] += offset
            for platform in levels.lava:
                platform[0] += offset
            for platform in levels.moving_platforms:
                platform[0] += offset

        shock_wave_timer += 1
        if shock_wave_timer > 1000:
            if total_wave == 0:
                total_wave += 1
                wave_timer_sound.play()
            shock_wave_timer = 0

        if player.shock:
            stick_power.combined_dimension[0] = 30
            total_wave = 0

        pygame.display.update()
        clock.tick(120)


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
while True:

    play = False
    Quit = False

    alpha = 0

    fade_surf = pygame.Surface(SCREEN_SIZE)
    fade_surf.fill((0, 0, 0))
    white = (255, 255, 255)
    grey = (128, 128, 128)
    blue = (0, 191, 255)
    pink = (255, 0, 127)
    yellow = (255, 255, 0)
    red = (255, 0, 0)
    green = (0, 255, 0)
    tor = (64, 224, 208)

    main_menu_surf = pygame.Surface(SCREEN_SIZE)
    instruction_surf = pygame.Surface(SCREEN_SIZE)
    animation_surf = pygame.Surface(SCREEN_SIZE)

    instructions = [pygame.font.Font("data/impact.ttf", 30).render(
        'PLAYER CONTROLS:', True, tor), pygame.font.SysFont("Impact", 30).render('POWERS:', True, tor)]

    intro_surf = pygame.Surface(SCREEN_SIZE)
    intro = pygame.font.Font(
        "data/impact.ttf", 100).render('FIELD RUNNER', True, white)
    intro_timer = 0

    player_controls_surf = pygame.Surface((400, 400))
    player_powers_surf = pygame.Surface((400, 400))

    # ---------------------
    control_list = []
    up_1 = pygame.font.Font(
        "data/arial.ttf", 30).render('UP/DOUBLE JUMP : W', True, white)
    left_1 = pygame.font.Font(
        "data/arial.ttf", 30).render('LEFT : A', True, white)
    right_1 = pygame.font.Font(
        "data/arial.ttf", 30).render('RIGHT : D', True, white)
    click = pygame.font.Font(
        "data/arial.ttf", 30).render('FIRE : LEFT CLICK', True, white)
    control_list.append(up_1)
    control_list.append(left_1)
    control_list.append(right_1)
    control_list.append(click)
    # ---------------------
    power_list = []
    wave = pygame.font.Font(
        "data/arial.ttf", 30).render('SHOCK WAVE : M', True, white)
    stick = pygame.font.Font(
        "data/arial.ttf", 30).render('STICK : SPACE + HOLD(A/D)', True, white)

    power_list.append(wave)
    power_list.append(stick)

    # ---------------------

    start_option1 = pygame.font.Font(
        "data/impact.ttf", 40).render('START', True, tor)
    start_option2 = pygame.font.Font(
        "data/impact.ttf", 30).render('START', True, grey)

    instruction_option1 = pygame.font.Font(
        "data/impact.ttf", 40).render('INSTRUCTIONS', True, tor)
    instruction_option2 = pygame.font.Font(
        "data/impact.ttf", 30).render('INSTRUCTIONS', True, grey)

    quit_option1 = pygame.font.Font(
        "data/impact.ttf", 40).render('QUIT', True, tor)
    quit_option2 = pygame.font.Font(
        "data/impact.ttf", 30).render('QUIT', True, grey)

    options = [[start_option1, start_option2], [instruction_option1,
                                                instruction_option2], [quit_option1, quit_option2]]

    location = 0
    main_menu = True
    instruction_menu = False

    particle_list = []
    add = False
    explosion = False
    explosion_location = [0, 0]

    def explosion_effect(color):
        if add:
            particle_list.append([explosion_location[0], explosion_location[1], random.randint(
                50, 80), random.randint(50, 80), random.choice([-5, -4, -3, 0, 3, 4]), random.choice([-20, -6, 0])])
        for particle in particle_list:
            pygame.draw.rect(animation_surf, color, [
                             particle[0], particle[1], particle[2], particle[3]])
            particle[0] += particle[4]
            particle[1] += particle[5]
            particle[5] += 0.5
            particle[3] -= 0.5
            particle[2] -= 0.5
            if particle[2] <= 0 or particle[3] <= 0:
                particle_list.remove(particle)

    class square_class:
        def __init__(self):
            self.color = random.choice([blue, pink, yellow, red, green])
            self.dimension = [30, 30]
            self.square_rect = pygame.Rect(
                SCREEN_SIZE[0]/2, SCREEN_SIZE[1]-40, self.dimension[0], self.dimension[1])
            self.y_momentum = -10
            self.x_momentum = random.choice(
                [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5])
            self.square_surf = pygame.Surface(self.dimension)
            self.rate = random.choice([-1, 1])

        def draw(self, animation_surf):
            pygame.draw.rect(animation_surf, self.color, [
                             self.square_rect[0], self.square_rect[1], self.dimension[0], self.dimension[1]])

        def move(self):
            self.sqaure_movement = [0, 0]
            self.dimension[0] += 1
            self.dimension[1] += 1
            self.square_surf = pygame.Surface(self.dimension)
            self.square_surf.fill(blue)
            self.square_rect[1] += self.y_momentum
            self.y_momentum += 0.1

    length = 350

    time = 0

    square_list = []

    while not play:
        intro_timer += 1

        SCREEN.fill((0, 0, 0))

        if intro_timer <= 150:

            SCREEN.blit(intro_surf, (0, 0))
            intro_surf.blit(intro, (350, 200))
            if length > 880:
                length = 350
            length += 4.5
            pygame.draw.line(SCREEN, white, (350, 320), (int(length), 320), 3)

            fade_surf.set_alpha(alpha)
            SCREEN.blit(fade_surf, (0, 0))
            alpha += 2
            pygame.time.delay(30)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and location == 1:
                    main_menu = False
                    instruction_menu = True

                if event.key == pygame.K_RETURN and location == 0:
                    main_menu = False
                    instruction_menu = False
                    play = True

                if event.key == pygame.K_RETURN and location == 2:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_BACKSPACE:
                    main_menu = True
                    instruction_menu = False

                if event.key == pygame.K_UP:
                    if main_menu:
                        location -= 1

                if event.key == pygame.K_DOWN:
                    if main_menu:
                        location += 1

        if intro_timer > 150:
            time += 1

            # ------------------------background_animation------------------------------------
            if len(square_list) < 1:
                square_list.append(square_class())

            if main_menu:
                i = 0
                spacing = 0

                if location < 0:
                    location = 2
                if location > 2:
                    location = 0

                SCREEN.blit(main_menu_surf, (0, 0))
                for option in options:
                    if i == location:
                        SCREEN.blit(option[0], (900, 400+spacing))
                    else:
                        SCREEN.blit(option[1], (900, 400+spacing))
                    i += 1
                    spacing += 100

            if instruction_menu:

                t = 0
                for i in control_list:
                    SCREEN.blit(i, (150, 200+t))
                    t += 100

                t = 0
                for i in power_list:
                    SCREEN.blit(i, (750, 200+t))
                    t += 100
                i = 0
                spacing = 0
                pygame.draw.line(SCREEN, tor, (600, 100), (600, 600), 1)
                for instruction in instructions:
                    SCREEN.blit(instruction, (100+spacing, 100))
                    i += 1
                    spacing += 600

            for square in square_list:

                square.move()
                square.draw(animation_surf)
                if square.dimension[0] > 150:
                    explosion = True
                    add = True
                    color = square.color
                    explosion_location = [
                        square.square_rect.center[0], square.square_rect.center[1]]
                    square_list.remove(square)
                    break

            if explosion:
                explosion_effect(color)

            if time > 4:
                time = 0
                add = False
            animation_surf.set_alpha(70)
            SCREEN.blit(animation_surf, (0, 0))
            animation_surf.fill((0, 0, 0))

        pygame.display.update()
        clock.tick(60)

    alpha = 0

    if play:
        while alpha < 300:
            fade_surf.set_alpha(alpha)
            SCREEN.blit(fade_surf, (0, 0))
            alpha += 10
            pygame.time.delay(50)
            pygame.display.update()
            clock.tick(60)

    if play:
        main()
        alpha = 0
        pygame.mixer.music.fadeout(2000)
        while alpha < 300:
            fade_surf.set_alpha(alpha)
            SCREEN.blit(fade_surf, (0, 0))
            alpha += 10
            pygame.time.delay(50)
            pygame.display.update()
            clock.tick(120)
