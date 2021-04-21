# imports
import random

import pygame
from pygame import mixer

# init
pygame.init()

# window and screen
window = pygame.display
window.set_caption("Space Invader")
game_icon = pygame.image.load("sprites/images/logo.png")
window.set_icon(game_icon)
width, height = 600, 800
screen = window.set_mode((width, height))
margin = 15

# load sprites/images
PLAYER = pygame.image.load("sprites/images/player.png")
LASER_PLAYER = pygame.image.load("sprites/images/laser_player.png")

ENEMY_red = pygame.image.load("sprites/images/enemy_red.png")
ENEMY_green = pygame.image.load("sprites/images/enemy_green.png")
ENEMY_blue = pygame.image.load("sprites/images/enemy_blue.png")
ENEMY_yellow = pygame.image.load("sprites/images/enemy_yellow.png")
ENEMY_purple = pygame.image.load("sprites/images/enemy_purple.png")
ENEMY_orange = pygame.image.load("sprites/images/enemy_orange.png")

LASER_red = pygame.image.load("sprites/images/laser_red.png")
LASER_green = pygame.image.load("sprites/images/laser_green.png")
LASER_blue = pygame.image.load("sprites/images/laser_blue.png")
LASER_yellow = pygame.image.load("sprites/images/laser_yellow.png")
LASER_purple = pygame.image.load("sprites/images/laser_purple.png")
LASER_orange = pygame.image.load("sprites/images/laser_orange.png")

BG = pygame.transform.scale(pygame.image.load('sprites/images/background.png'), (screen.get_width(), screen.get_height()))
LIFE = pygame.image.load("sprites/images/heart.png")
EXTRA_LIFE = pygame.transform.scale(LIFE, (48, 48))

COINS = *(pygame.image.load(f"sprites/images/coin{i + 1}.png") for i in range(6)),
coin_timer = 0
coin_count = 0

EXPLOSIONS = *(pygame.image.load(f"sprites/images/explosion{i + 1}.png") for i in range(16)),

# music and sound
laser_player = mixer.Sound("sprites/music/laser_player.wav")
laser_enemy = mixer.Sound("sprites/music/laser_enemy.wav")
explode_player = mixer.Sound("sprites/music/explode_player.wav")
explode_enemy = mixer.Sound("sprites/music/explode_enemy.wav")
health_lost = mixer.Sound("sprites/music/health_lost.wav")
gain_player = mixer.Sound("sprites/music/coin_gain.wav")
life_lost = mixer.Sound("sprites/music/life_lost1.wav")
mixer.music.load("sprites/music/Background - Hans Zimmer.mp3")

# pens
big_pen = pygame.font.SysFont("comicsans", 50)
medium_pen = pygame.font.SysFont("comicsans", 40)
small_pen = pygame.font.SysFont("comicsans", 30)
tiny_pen = pygame.font.SysFont("comicsans", 20)

lost_label = big_pen.render("You Lost !!!", True, (255, 0, 0))
new_game_label = medium_pen.render("Press enter to start a new game!", True, (0, 255, 0))
paused_label = big_pen.render("Game Paused", True, (255, 255, 0))
continue_label = medium_pen.render("Press p to continue the game!", True, (255, 255, 0))
level_passed_label = big_pen.render("LEVEL PASSED", True, (0, 255, 0))

# initialize screen and running
screen.blit(BG, (0, 0))
mixer.music.play(-1)
screen.blit(new_game_label, ((screen.get_width() - new_game_label.get_width()) / 2,
                             screen.get_height() / 2 - new_game_label.get_height()))
window.update()


# Spaceship --> player, enemy, laser, coin, powerup
class Spaceship:
    speed = 3

    def __init__(self, img, cords, width=None, velocity=(0, 0)):
        if width:
            size = (width, int((width * img.get_height()) / img.get_width()) + 1)
            self.img = pygame.transform.scale(img, size)
        else:
            self.img = img
        self.x, self.y = cords
        self.vx, self.vy = velocity
        self.mask = pygame.mask.from_surface(self.img)
        screen.blit(self.img, (self.x, self.y))

    def move(self, restrictions=True):
        self.x += self.__class__.speed * self.vx
        self.y += self.__class__.speed * self.vy
        if restrictions: self.corrections()
        screen.blit(self.img, (self.x, self.y))

    def corrections(self):
        pass

    def die(self, lst, explode_sound=None):
        if sound and explode_sound: explode_sound.play()
        del lst[lst.index(self)]

    def collide(self, obj):
        dx = int(obj.x - self.x) + 1
        dy = int(obj.y - self.y) + 1
        return self.mask.overlap(obj.mask, (dx, dy))


class Laser(Spaceship):

    def __init__(self, img, cords, width=None, velocity=(0, -1)):
        super().__init__(img, cords, width, velocity)


class Player(Spaceship):
    health = 100

    def __init__(self, img=PLAYER, cords=((screen.get_width() - PLAYER.get_width()) / 2, - PLAYER.get_height() - 10),
                 width=64, velocity=(0, 0)):
        super().__init__(img, cords, width, velocity)
        self.cooldown = 0
        self.lasers = []
        self.weapon = 'basic'

    def draw_healthbar(self, size=(200, 15)):
        cords=(screen.get_width() - size[0] - margin, margin)
        x_val, y_val = cords
        length, width = size
        ratio = self.health / self.__class__.health
        draw_bar(cords, size, (255, 0, 0))
        if self.health: draw_bar((int(x_val + length * (1 - ratio)), y_val),
                                 (int(length * ratio) + 1, width), (0, 255, 0))

    def corrections(self):
        global in_a_row
        if self.x < 0:
            self.x = 0
        elif self.x > screen.get_width() - self.img.get_width():
            self.x = screen.get_width() - self.img.get_width()
        if self.y < 0:
            self.y = 0
        elif self.y > screen.get_height() - self.img.get_height():
            self.y = screen.get_height() - self.img.get_height()
        if self.cooldown: self.cooldown -= 1
        for laser in self.lasers:
            laser.move()
            if laser.y < 0:
                laser.die(self.lasers)
                in_a_row = 0
            else:
                for enemy in enemies[:]:
                    if laser.collide(enemy):
                        enemy.die()
                        laser.die(self.lasers)
                        break

    def shoot(self):
        if sound: laser_player.play()
        if self.weapon == 'basic':
            laser = Laser(LASER_PLAYER, (self.x + self.img.get_width() / 2 - LASER_PLAYER.get_width() / 2,
                                        self.y - LASER_PLAYER.get_height() / 2))
            self.lasers.append(laser)
            self.cooldown = int(FPS / level) + 1

    def get_damage(self, damage):
        if sound: health_lost.play()
        self.health -= damage
        if self.health < 0: self.health = 0

    def control(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.vx = -1
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.vx = 1
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.vy = -1
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.vy = 1
            elif event.key == pygame.K_SPACE and not self.cooldown:
                self.shoot()
        elif event.type == pygame.KEYUP:
            if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.vx == -1: self.vx = 0
            if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.vx == 1: self.vx = 0
            if (event.key == pygame.K_UP or event.key == pygame.K_w) and self.vy == -1: self.vy = 0
            if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and self.vy == 1: self.vy = 0

    def collect(self, thing):
        global lives
        if sound: gain_player.play()
        if thing.img == EXTRA_LIFE: lives = min(5, lives+1)
        elif thing.img == HEALTH: self.health = min(100, self.health + 15)
        elif thing.img == WEAPON: self.weapon = 'double'


class Enemy(Spaceship):
    lasers = []

    def __init__(self):
        color = random.choice(('red', 'blue', 'green', 'yellow', 'orange', 'purple'))
        width = 48
        cords = (random.randint(0, screen.get_width() - width), random.randint(-screen.get_width() * level // 2, -64))
        velocity = (random.choice((1, -1)) * random.randint(0, 800) / 1000, random.randint(50, 400) / 1000)
        super().__init__(eval(f"ENEMY_{color}"), cords, width, velocity)
        self.laser_img = eval(f"LASER_{color}")

    def corrections(self):
        global lives
        if self.x <= 0:
            self.x = 0
            self.randomize()
        elif self.x >= screen.get_width() - self.img.get_width():
            self.x = screen.get_width() - self.img.get_width()
            self.randomize()
        if self.y >= screen.get_height():
            if lives: lives -= 1
            self.die(gift=False)
        if random.randrange(1000) < 2: self.shoot()

    def randomize(self):
        self.vx = [-1, 1][self.vx < 0] * random.randint(0, 800) / 1000
        self.vy = random.randint(50, 200) / 1000

    def shoot(self):
        if sound: laser_enemy.play()
        laser1 = Laser(self.laser_img, (self.x - self.laser_img.get_width() / 2, self.y), velocity=(0, 1))
        laser2 = Laser(self.laser_img, (self.x + self.img.get_width() - self.laser_img.get_width() / 2, self.y),
                       velocity=(0, 1))
        Enemy.lasers.append(laser1)
        Enemy.lasers.append(laser2)

    def die(self, gift=True):
        global in_a_row
        if self.y >= screen.get_height(): track = life_lost
        else: track = explode_enemy
        super().die(enemies, track)
        if gift:
            in_a_row += 1
            rarity = random.randrange(10)
            if rarity < 3 and lives < 5:
                power_ups.append(PowerUp((self.x, self.y), EXTRA_LIFE))
            else:
                coins.append(Coin((self.x - self.img.get_width()/2 + COINS[0].get_width()/2, self.y)))
        else:
            in_a_row = 0


class Coin(Spaceship):

    def __init__(self, cords):
        super().__init__(img=COINS[coin_timer // 10], cords=cords, width=None, velocity=(0, 1))
        self.val = in_a_row

    def corrections(self):
        global coin_timer
        self.x += self.img.get_width() / 2
        self.img = COINS[coin_timer // 10]
        self.x -= self.img.get_width() / 2
        if self.x < 0:
            self.x = 0
        if self.x >= screen.get_width() - COINS[0].get_width():
            self.x = screen.get_width() - COINS[0].get_width()
        if self.y >= screen.get_height():
            self.die(coins)


class PowerUp(Spaceship):

    def __init__(self, cords, img):
        super().__init__(img, cords=cords, width=None, velocity=(0, 1))

    def corrections(self):
        if self.x < 0:
            self.x = 0
        if self.x >= screen.get_width() - COINS[0].get_width():
            self.x = screen.get_width() - COINS[0].get_width()
        if self.y >= screen.get_height():
            self.die(power_ups)




# some function definitions
def draw_bar(cords, size, color):
    width, height = size
    a = width - height
    r = height / 2
    x, y = cords
    pygame.draw.circle(screen, color, (x + r, y + r), height / 2)
    pygame.draw.circle(screen, color, (x + a + r, y + r), height / 2)
    pygame.draw.rect(screen, color, (x + height / 2, y, a, height))


def draw_lives(gap=margin - 5):
    for life in range(lives):
        screen.blit(LIFE, (gap + life * LIFE.get_width(), gap))


def draw_coins(gap=margin):
    global coin_timer
    coin_label = small_pen.render(f"x{coin_count}", True, (255, 255, 255))
    draw_bar((gap, 2.5 * gap + LIFE.get_height()),
             (3 * gap + COINS[0].get_width() + coin_label.get_width(), COINS[0].get_height() - gap),
             (255, 255, 255))
    draw_bar((gap + 2, 2.5 * gap + LIFE.get_height() + 2),
             (3 * gap + COINS[0].get_width() + coin_label.get_width() - 4, COINS[0].get_height() - gap - 4),
             (0, 0, 0))
    screen.blit(COINS[coin_timer // 10], (1.8 * gap + (COINS[0].get_width() - COINS[coin_timer // 10].get_width()) / 2,
                                          2 * gap + LIFE.get_height()))
    screen.blit(coin_label, (2.5 * gap + COINS[0].get_width(), 3 * gap + LIFE.get_height()))
    if in_a_row > 1:
        in_a_row_label = tiny_pen.render(f"{in_a_row}x in a row", True, (0, 255, 0))
        screen.blit(in_a_row_label, (3 * gap, 2 * gap + LIFE.get_height() + COINS[0].get_height()))
    coin_timer = (coin_timer + 1) % FPS


# update bar status
def update_bars(restrictions=True):
    draw_lives()
    draw_coins()
    player.draw_healthbar()
    level_label = small_pen.render(f"Level: {level}", True, (255, 255, 255))
    level_pos = (screen.get_width() - level_label.get_width() - margin, 2.5 * margin)
    screen.blit(level_label, level_pos)
    enemy_count = small_pen.render(f"Kills: {[5 * level - len(enemies), 0][teleported]} / {5 * level}", True,
                                   (255, 255, 255))
    enemy_count_pos = (screen.get_width() - enemy_count.get_width() - margin, level_pos[1] + level_label.get_height() + margin//2)
    screen.blit(enemy_count, enemy_count_pos)


# game continues
def proceed():
    screen.blit(BG, (0, 0))
    for enemy in enemies: enemy.move()
    for power_up in power_ups: power_up.move()
    for laser in Enemy.lasers:
        laser.move()
        if laser.y > screen.get_height():
            laser.die(Enemy.lasers)
    for coin in coins: coin.move()


# check collisions:
def check_collisions():
    global coin_count, lives
    for enemy in enemies[:]:
        if enemy.collide(player):
            player.get_damage(10)
            enemy.die(False)

    for coin in coins[:]:
        if coin.collide(player):
            if sound: gain_player.play()
            coin.die(coins)
            coin_count += coin.val

    for power_up in power_ups[:]:
        if power_up.collide(player):
            player.collect(power_up)
            power_up.die(power_ups)

    for laser in Enemy.lasers[:]:
        if laser.collide(player):
            player.get_damage(5)
            laser.die(Enemy.lasers)


# game paused
def pause_screen():
    screen.blit(paused_label, ((screen.get_width() - paused_label.get_width()) / 2,
                               screen.get_height() / 2 - 2 * paused_label.get_height()))
    screen.blit(continue_label, ((screen.get_width() - continue_label.get_width()) / 2,
                                 screen.get_height() / 2))


def level_up():
    global teleported, level, coin_count, in_a_row
    cx = screen.get_width() / 2 - 32
    cy = screen.get_height() * 2 / 3 - 32
    Coin.speed = PowerUp.speed = 0

    if not (teleported and (player.x, player.y) == (cx, cy)):
        if player.y < - player.img.get_height():
            if level:
                player.y = 1.5 * screen.get_height()
            else:
                player.y = screen.get_height() + 2 * player.img.get_height()
            teleported = True
            level += 1
            Enemy.lasers.clear()
            player.lasers.clear()
            while len(coins):
                if sound: gain_player.play()
                coin_count += coins.pop().val
            while len(power_ups):
                player.collect(power_ups.pop())
            in_a_row = 0

        player.vy = -1

        if player.x > cx:
            player.vx = -1
        elif player.x < cx:
            player.vx = 1

        if abs(cx - player.x) < player.speed:
            player.x = cx
            player.vx = 0
        if abs(cy - player.y) < player.speed and teleported:
            player.y = cy
            player.vy = 0

        if teleported:
            new_level_label = big_pen.render(f"LEVEL: {level}", True, (0, 255, 0))
            screen.blit(new_level_label, ((screen.get_width() - new_level_label.get_width()) / 2,
                                          screen.get_height() / 2 - new_level_label.get_height()))
            player.health += 1
            if player.health > 100: player.health = 100
        else:
            screen.blit(level_passed_label, ((screen.get_width() - level_passed_label.get_width()) / 2,
                                             screen.get_height() / 2 - level_passed_label.get_height()))

    else:
        if player.health == 100:
            Spaceship.speed += ACC
            for _ in range(5 * level): enemies.append(Enemy())
            Coin.speed = PowerUp.speed = Spaceship.speed
        else:
            player.health += 1
            if player.health > 100: player.health = 100
            if len(coins):
                coin_count += coins[-1].val
                coins[-1].die(coins)


def main():

    global player, enemies, coins, power_ups
    global running, music, sound, level, lives, teleported, coin_count, in_a_row
    
    # initialise vars
    player = Player()
    player.health = 1
    enemies = []
    Enemy.lasers = []
    coins = []
    power_ups = []
    coin_count = 0
    in_a_row = 0
    explosion_timer = 0
    level = 0
    lives = 5
    paused = False
    teleported = False

    # game-loop:
    while True:
        window.update()
        clock.tick(FPS)

        # event control
        for eve in pygame.event.get():
            if eve.type == pygame.QUIT:
                pygame.quit()
                running = False
                return
            elif eve.type == pygame.KEYDOWN:
                if eve.key == pygame.K_m:
                    music = not music
                    if music:
                        mixer.music.unpause()
                    else:
                        mixer.music.pause()
                if eve.key == pygame.K_n:
                    sound = not sound
                if eve.key == pygame.K_p and not explosion_timer:
                    paused = not paused
                if paused or not len(enemies): break
            if len(enemies) and not explosion_timer: player.control(eve)

        # paused screen
        if paused:
            pause_screen()
            continue

        # continue on-going game
        proceed()
        player.move(len(enemies))
        update_bars()

        # lost animation: yet to do
        if not (lives and player.health):
            if sound and not explosion_timer:
                explode_player.play()
                player.vx = player.vy = 0
            stable = 10
            player.img = pygame.transform.scale(EXPLOSIONS[explosion_timer // stable], (100, 100))
            explosion_timer = explosion_timer + 1
            if explosion_timer // stable > len(EXPLOSIONS) - 1: break
            continue

        # level up animation
        if not len(enemies):
            level_up()
            continue
        teleported = False

        # collision control
        check_collisions()

    screen.blit(lost_label, ((screen.get_width() - lost_label.get_width()) / 2,
                             screen.get_height() / 2 - 2 * lost_label.get_height()))
    screen.blit(new_game_label, ((screen.get_width() - new_game_label.get_width()) / 2,
                                 screen.get_height() / 2))
    window.update()


ACC = 0.2
FPS = 60
clock = pygame.time.Clock()
running = True
music = True
sound = True

# mainloop
while running:
    for eve in pygame.event.get():
        if eve.type == pygame.QUIT:
            running = False
        elif eve.type == pygame.KEYDOWN:
            if eve.key == pygame.K_m:
                music = not music
                if music:
                    mixer.music.unpause()
                else:
                    mixer.music.pause()
            if eve.key == pygame.K_n:
                sound = not sound
            if eve.key == pygame.K_RETURN:
                main()

# TODO: make score animation
# TODO: create the concept of high score in different fields (enemies killed, coins collected)
# TODO: modify extra lives, health, better lasers to collect from the screen
# TODO: create a proper main menu
