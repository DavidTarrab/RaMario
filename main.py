import pygame
from pygame.locals import *
import sys
import random
 
pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional
 
HEIGHT = 600
WIDTH = 800
FPS = 60
GRAV = 1.2
 
FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__() 
		self.surf = pygame.Surface((40, 40))
		self.surf.fill((128,255,40))
		self.rect = self.surf.get_rect()
   
		self.pos = vec((10, 385))
		self.vel = vec(0,0)
		self.acc = vec(0,0)

		self.facingRight = True
		self.scroll = False
		self.running = False
		self.moving = False
		self.collisions = []
		self.jumpable = False

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

	def checkCollision(self, platform):
		self.collisions = []
		hits = pygame.sprite.spritecollide(P1 , platforms, False)
		for platform in hits:
			if self.rect.bottom >= platform.rect.top and self.rect.bottom <= platform.rect.bottom:
				self.collisions.append((platform, 'bottom'))
			elif self.rect.top <= platform.rect.bottom and self.rect.top >= platform.rect.top:
				self.collisions.append((platform, 'top'))
			elif self.rect.left <= platform.rect.right and self.rect.left >= platform.rect.left:
				self.collisions.append((platform, 'right'))
			elif self.rect.right >= platform.rect.left and self.rect.right <= platform.rect.right:
				self.collisions.append((platform, 'left'))

	def update(self):
		self.acc = vec(0, GRAV)
		self.running = False
		self.moving = False
		self.jumpable = False

		for platform in platforms:
			self.checkCollision(platform)

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
				self.acc.x = -0.6
			elif self.vel.x < 0:
				self.vel.x = 0
				self.acc.x = 0
		# Deceleration on left facing
		elif not self.moving and not self.facingRight:
			if self.vel.x < 0:
				self.acc.x = 0.6
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
		for collision in self.collisions:
			if collision[1] == 'bottom' and not self.vel.y < 0:
				self.pos.y = collision[0].rect.top + 1
				self.vel.y = 0
				self.jumpable = True
			if collision[1] == 'top':
				self.pos.y = collision[0].rect.bottom + 30
				self.vel.y = 0
			if collision[1] == 'right':
				self.pos.x = collision[0].rect.left - 30
				self.vel.x = 0
			if collision[1] == 'left':
				self.pos.x = collision[0].rect.right + 1
				self.vel.x = 0

		# Update actual position of the sprite
		self.rect.bottomleft = self.pos

	def jump(self):
		if self.jumpable:
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
 
floor = platform(WIDTH*8, 80, WIDTH*4, HEIGHT - 40)

P1 = Player()

all_sprites = pygame.sprite.Group()
all_sprites.add(floor)
all_sprites.add(P1)

platforms = pygame.sprite.Group()
platforms.add(floor)
for x in range(random.randint(5, 10)):
	pl = platform(40, 40, random.randint(100, WIDTH*5), random.randint(50, 500))
	platforms.add(pl)
	all_sprites.add(pl)

while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:    
			if event.key == pygame.K_UP:
				P1.jump()
	 
	displaysurface.fill((0,0,0))
 
	P1.update()
	for entity in all_sprites:
		displaysurface.blit(entity.surf, entity.rect)

	pygame.display.update()
	FramePerSec.tick(FPS)
