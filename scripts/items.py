
import pygame
from scripts.spark import Spark
import random
import math

class Item:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.animation = self.game.assets['items' + '/' + self.type].copy()
        self.flip = False
        self.spark = 120
        self.destroy = False
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def effect(self):
        pass
    
    def update(self):
        
        self.spark -= 1
        self.animation.update()
        
        if not self.spark:
            self.game.sparks.append(Spark((self.pos[0] + 7, self.pos[1] + 7), random.random() - 0.5  , 1 + random.random()))
            self.game.sparks.append(Spark((self.pos[0] + 7, self.pos[1] + 7), random.random() - 0.5 + math.pi / 2 , 1 + random.random()))
            self.game.sparks.append(Spark((self.pos[0] + 7, self.pos[1] + 7), random.random() - 0.5 + math.pi , 1 + random.random()))
            self.game.sparks.append(Spark((self.pos[0] + 7, self.pos[1] + 7), random.random() - 0.5 - math.pi / 2 , 1 + random.random()))
            self.spark = 120
        
        if self.rect().colliderect(self.game.player.rect()):
            
            self.effect()
            self.destroy = True
            
        
     
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))


class DoubleJump(Item):
    
    def __init__(self,  game, pos, size):
        super().__init__(game, 'doublejump', pos, size)
    
    def effect(self):
        self.game.player.abilities.set_double_jump_unlocked()
        return True
     
    def update(self):
        super().update()
        if self.destroy:
            return True
        
class Dash(Item):
    
    def __init__(self,  game, pos, size):
        super().__init__(game, 'dash', pos, size)
    
    def effect(self):
        self.game.player.abilities.set_dash_unlocked()
        return True
     
    def update(self):
        super().update()
        if self.destroy:
            return True
        
class WallSlide(Item):
    
    def __init__(self,  game, pos, size):
        super().__init__(game, 'wallslide', pos, size)
    
    def effect(self):
        self.game.player.abilities.set_wall_slide_unlocked()
        return True
     
    def update(self):
        super().update()
        if self.destroy:
            return True
        
class WallJump(Item):
    
    def __init__(self,  game, pos, size):
        super().__init__(game, 'walljump', pos, size)
    
    def effect(self):
        self.game.player.abilities.set_wall_jump_unlocked()
        return True
     
    def update(self):
        super().update()
        if self.destroy:
            return True
        
class TimeStop(Item):
    
    def __init__(self,  game, pos, size):
        super().__init__(game, 'timestop', pos, size)
    
    def effect(self):
        self.game.player.abilities.set_time_stop_unlocked()
        return True
     
    def update(self):
        super().update()
        if self.destroy:
            return True