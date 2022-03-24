import pygame
from pygame.locals import *
import sys
import random
 
pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional
 
HEIGHT = 450
WIDTH = 400
FPS = 60
GRAV = .8
 
FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__() 
		self.surf = pygame.Surface((30, 30))
		self.surf.fill((128,255,40))
		self.rect = self.surf.get_rect()
   
		self.pos = vec((10, 385))
		self.vel = vec(0,0)
		self.acc = vec(0,0)

	def walkRight(self):
		self.acc.x = 1.1
		if self.vel.x >= 10:
			self.vel.x = 10

	def walkLeft(self):
		self.acc.x = -1.1
		if self.vel.x <= -10:
			self.vel.x = -10

	def move(self):
		self.acc = vec(0,GRAV) 

		self.acc.x += self.vel.x * FRIC
		self.vel += self.acc
		self.pos += self.vel + 0.5 * self.acc
		self.jumping = False
	 
		self.rect.midbottom = self.pos
	
	def update(self):
		pressed_keys = pygame.key.get_pressed()
		if pressed_keys[K_RIGHT]:
			walkRight()
		if pressed_keys[K_LEFT]:
			walkLeft()

		hits = pygame.sprite.spritecollide(P1 , platforms, False)
		if hits:
			if P1.vel.y > 0:
				self.pos.y = hits[0].rect.top + 1
			if P1.vel.y < 0:
				self.pos.y = hits[0].rect.bottom + 30
			self.vel.y = 0

	def jump(self):
		hits = pygame.sprite.spritecollide(self, platforms, False)
		if hits:
			self.vel.y = -18
 
class platform(pygame.sprite.Sprite):
	def __init__(self, width, height, x, y):
		super().__init__()
		self.width = width
		self.height = height
		self.x = x
		self.y = y
		self.surf = pygame.Surface((width, height))
		self.surf.fill((255,0,0))
		self.rect = self.surf.get_rect(center = (x, y))
 
PT1 = platform(WIDTH*10, 20, WIDTH*10/2, HEIGHT - 10)

P1 = Player()

all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)

platforms = pygame.sprite.Group()
platforms.add(PT1)
for x in range(random.randint(5, 6)):
	pl = platform(random.randint(50,100), 12, random.randint(0,WIDTH-10), random.randint(0, HEIGHT-30))
	platforms.add(pl)
	all_sprites.add(pl)

while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:    
			if event.key == pygame.K_SPACE:
				P1.jump()

	if P1.rect.right >= WIDTH / 3:
		P1.pos.x -= abs(P1.vel.x)
		for plat in platforms:
			plat.rect.x -= abs(P1.vel.x)
			if plat.rect.right <= 0:
				plat.kill()
	 
	displaysurface.fill((0,0,0))
 
	P1.move()
	P1.update()
	print(P1.vel.x)
	for entity in all_sprites:
		displaysurface.blit(entity.surf, entity.rect)

	pygame.display.update()
	FramePerSec.tick(FPS)
