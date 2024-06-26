import sys
import math
import random
import os

import threading
import pygame
import asyncio

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Gunman, Slime, Goblin, Spirit
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.items import DoubleJump, Dash, WallSlide, WallJump, TimeStop, Gun



class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Pygame platformer')
        #self.screen = pygame.display.set_mode((640, 480))
        self.screen = pygame.display.set_mode((1280, 960))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'traps' : load_images('tiles/traps'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.jpg'),
            'clouds': load_images('clouds'),
            'items/doublejump' : Animation(load_images('items/doublejump'), img_dur=6),
            'items/dash' : Animation(load_images('items/dash'), img_dur=6),
            'items/wallslide' : Animation(load_images('items/wallslide'), img_dur=6),
            'items/walljump' : Animation(load_images('items/walljump'), img_dur=6),
            'items/timestop' : Animation(load_images('items/timestop'), img_dur=6),
            'items/gun' : Animation(load_images('items/gun'), img_dur=6),
            'enemy/idle' : Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run' : Animation(load_images('entities/enemy/run'), img_dur=4),
            'slime/idle': Animation(load_images('entities/slime/idle'), img_dur=6),
            'slime/run': Animation(load_images('entities/slime/run'), img_dur=6),
            'goblin/idle': Animation(load_images('entities/goblin/idle'), img_dur=10),
            'goblin/run': Animation(load_images('entities/goblin/run'), img_dur=8),
            'spirit/idle': Animation(load_images('entities/spirit/idle'), img_dur=8),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image("projectile.png"),
        }

        self.sfx = {
            'jump':pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash':pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit':pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot':pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience':pygame.mixer.Sound('data/sfx/ambience.wav'),
        }

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['jump'].set_volume(0.7)
        
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        self.level = 1
        
        self.load_level(self.level)

        self.screen_shake = 0

        self.max_time = 600
        self.time = 600
        self.time_stop = False

        self.game_run = True
        
        
    def load_level(self, map_id):

        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
    
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1), ('spawners', 2), ('spawners', 3), ('spawners', 4)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.dead = 0
            if spawner['variant'] == 1:
                self.enemies.append(Gunman(self, spawner['pos'], (8, 15)))
            if spawner['variant'] == 2:
               self.enemies.append(Slime(self, spawner['pos'], (16, 8)))
            if spawner['variant'] == 3:
               self.enemies.append(Goblin(self, spawner['pos'], (13, 18)))
            if spawner['variant'] == 4:
               self.enemies.append(Spirit(self, spawner['pos'], (13, 18)))
        
        self.items = []
        for item in self.tilemap.extract([('items', 0), ('items', 1), ('items', 2), ('items', 3), ('items', 4), ('items', 5)]):
            if item['variant'] == 0:
                self.items.append(DoubleJump(self, item['pos'], (16,16)))
            if item['variant'] == 1:
                self.items.append(Dash(self, item['pos'], (16,16)))
            if item['variant'] == 2:
                self.items.append(WallSlide(self, item['pos'], (16,16)))
            if item['variant'] == 3:
                self.items.append(WallJump(self, item['pos'], (16,16)))
            if item['variant'] == 4:
                self.items.append(TimeStop(self, item['pos'], (16,16)))
            if item['variant'] == 5:
                self.items.append(Gun(self, item['pos'], (16,16)))
                
        

        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        self.scroll = [0, 0]
        self.hit = False
        self.hit_guard = False
        self.dead = 0
        self.transition = -30

        self.time_stop = False
        self.time = 600
        
        self.player.abilities.reload()

    def play_music(self, music):
        pygame.mixer.music.load(music)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    
            
    
        
    def run(self):
        
        thread = threading.Thread(target=self.play_music, args=('data/music.wav',))
        thread.start()

        self.sfx['ambience'].play(-1)

        while self.game_run:
            self.display.blit(self.assets['background'], (0, 0))

            self.screen_shake = max(0, self.screen_shake - 1)

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps'))-1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            if self.player.abilities.time_stop_unlocked:
                if self.time_stop:
                    if self.time > 0:
                        self.time -= 1
                        if self.time < 50:
                            pass
                    else:
                        self.time_stop = False
                else:
                    self.time = min(self.max_time, self.time + 0.5)


            if self.hit and not self.hit_guard:
                
                self.hit_guard = True
                self.dead += 1

                self.sfx['hit'].play()
                self.screen_shake = max(16, self.screen_shake)

                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                    self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0,7)))
            

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition =  min(self.transition + 1, 30)
                if self.dead > 40:
                    self.load_level(self.level)
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            for rect in self.leaf_spawners:
               
                if random.random() * 49999 < rect.width * rect.height:
                    
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            
            if not self.time_stop:
                self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            
            asyncio.run(self.tilemap.render(self.display, offset=render_scroll))
            
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0,0 ))
                enemy.render(self.display, offset = render_scroll)
                if kill:
                    self.enemies.remove(enemy)
            
            
            

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)
            
            for projectile in self.projectiles.copy():
                if not self.time_stop:
                    projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                            self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if projectile[3] == 0:
                        if self.player.rect().collidepoint(projectile[0]):
                            self.projectiles.remove(projectile)
                            self.hit = True
                       
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, render_scroll)
                if kill:
                    self.sparks.remove(spark)
                    
            for item in self.items.copy():
                destroy = item.update()
                item.render(self.display, offset = render_scroll)
                if destroy:
                    print('jajo')
                    self.items.remove(item)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            if self.player.abilities.time_stop_unlocked:
                pygame.draw.rect(self.display, "black", (1,1,104,12))
                pygame.draw.rect(self.display, "red", (3,3,100,8))
                pygame.draw.rect(self.display, "blue", (3,3,100 * (self.time/self.max_time),8))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_run = False
                    thread.join()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_LSHIFT:
                        self.player.dash()
                    if event.key == pygame.K_j:
                        self.player.shoot()
                    if event.key == pygame.K_t:
                        if self.player.abilities.time_stop_unlocked:
                            self.time_stop = not self.time_stop
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
            
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255,255,255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255,255,255))
                self.display.blit(transition_surf, (0,0))

            screen_shake_offset = (random.random() * self.screen_shake - self.screen_shake / 2, random.random() * self.screen_shake - self.screen_shake / 2)
            

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screen_shake_offset)
            pygame.display.update()
            self.clock.tick(60)

Game().run()