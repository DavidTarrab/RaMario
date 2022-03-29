import pygame
from pygame.locals import *
import sys
import random
 
pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional
 
HEIGHT = 450
WIDTH = 400
FPS = 60
GRAV = 1.2
 
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

		self.facingRight = True
		self.scroll = False
		self.running = False
		self.moving = False

	def walkRight(self):
		self.acc.x = 0.8
		self.facingRight = True
		self.moving = True

	def walkLeft(self):
		self.acc.x = -0.8
		self.facingRight = False
		if self.vel.x <= 0:
			self.scroll = False
		self.moving = True

	def runRight(self):
		self.acc.x = 1.2
		self.facingRight = True
		self.running = True
		self.moving = True

	def runLeft(self):
		self.acc.x = -1.2
		self.facingRight = False
		if self.vel.x <= 0:
			self.scroll = False
		self.running = True
		self.moving = True

	def update(self):
		self.acc = vec(0, GRAV)
		self.running = False
		self.moving = False

		# Get key presses
		pressed_keys = pygame.key.get_pressed()
		# Trigger movement with key presses
		if pressed_keys[K_LSHIFT]:
			if pressed_keys[K_RIGHT]:
				self.runRight()
			elif pressed_keys[K_LEFT]:
				self.runLeft()
		elif not pressed_keys[K_LSHIFT]:
			if pressed_keys[K_RIGHT]:
				self.walkRight()
			elif pressed_keys[K_LEFT]:
				self.walkLeft()
		# Deceleration on right facing
		if not self.moving and self.facingRight:
			if self.vel.x > 0:
				self.acc.x = -0.4
			elif self.vel.x < 0:
				self.vel.x = 0
				self.acc.x = 0
		# Deceleration on left facing
		elif not self.moving and not self.facingRight:
			if self.vel.x < 0:
				self.acc.x = 0.4
			elif self.vel.x > 0:
				self.vel.x = 0
				self.acc.x = 0

		# Update the velocity and position using kinematics
		self.vel += self.acc
		self.pos.y += self.vel.y + 0.5 * self.acc.y
		if not self.scroll:
			self.pos.x += self.vel.x + 0.5 * self.acc.x

		# Left border
		if self.pos.x < 0:
			self.pos.x = 0

		# Speed cap
		if self.running:
			if self.vel.x >= 11:
				self.vel.x = 11
			if self.vel.x <= -11:
				self.vel.x = -11
		else:
			if self.vel.x >= 8:
				self.vel.x = 8
			if self.vel.x <= -8:
				self.vel.x = -8

		# Scrolling
		if self.rect.right >= WIDTH / 3:
			self.scroll = True
			for plat in platforms:
				plat.rect.x -= abs(self.vel.x)
				if plat.rect.right <= 0:
					plat.kill()

		# Collision detection
		hits = pygame.sprite.spritecollide(P1 , platforms, False)
		if hits:
			if P1.vel.y > 0:
				self.pos.y = hits[0].rect.top + 1
				self.vel.y = 0
			if P1.vel.y < 0 and not self.pos.y < hits[0].rect.top:
				self.pos.y = hits[0].rect.bottom + 30
				self.vel.y = 0

		# Update actual position of the sprite
		self.rect.bottomleft = self.pos

	def jump(self):
		hits = pygame.sprite.spritecollide(self, platforms, False)
		if hits:
			self.vel.y = -23
 
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
for x in range(random.randint(5, 10)):
	pl = platform(random.randint(50,100), 12, random.randint(100,WIDTH*5), random.randint(50, HEIGHT-50))
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
	 
	displaysurface.fill((0,0,0))
 
	P1.update()
	for entity in all_sprites:
		displaysurface.blit(entity.surf, entity.rect)

	pygame.display.update()
	FramePerSec.tick(FPS)
