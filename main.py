import pygame
from pygame.locals import *
import sys
import random
import math
 
pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional
 
HEIGHT = 380
WIDTH = 500
FPS = 60
GRAV = 0.8
SIDE = 32
 
FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.sprite = "stand"

		self.surf = pygame.image.load("Sprites/" + self.sprite + ".png").convert()
		self.surf.set_colorkey((255, 255, 255), RLEACCEL)
		self.rect = self.surf.get_rect()
   
		self.pos = vec((10, HEIGHT - 104))
		self.vel = vec(0,0)
		self.acc = vec(0,0)

		self.facing = 1
		self.scroll = False
		self.running = False
		self.moving = False
		self.collisions = []
		self.jumpable = False
		self.movingFrames = 0
		self.inAir = True
		self.dying = False

	def walk(self):
		self.acc.x = self.facing * 0.4
		if self.facing == -1 and self.vel.x < 0:
			self.scroll = False
		self.moving = True

	def run(self):
		self.acc.x = self.facing * 0.4
		if self.facing == -1 and self.vel.x < 0:
			self.scroll = False
		self.running = True
		self.moving = True

	def checkCollision(self):
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
		if not self.dying:
			self.acc = vec(0, GRAV)
		self.running = False
		self.moving = False
		self.jumpable = False
		self.inAir = True

		self.checkCollision()
		self.checkDamage()

		# Get key presses
		pressed_keys = pygame.key.get_pressed()
		# Trigger movement with key presses
		if not self.dying:
			if pressed_keys[K_LSHIFT]:
				if pressed_keys[K_RIGHT]:
					self.facing = 1
					self.run()
				elif pressed_keys[K_LEFT]:
					self.facing = -1
					self.run()
			elif not pressed_keys[K_LSHIFT]:
				if pressed_keys[K_RIGHT]:
					self.facing = 1
					self.walk()
				elif pressed_keys[K_LEFT]:
					self.facing = -1
					self.walk()

			# Collision detection
			for collision in self.collisions:
				if collision[1] == 'bottom' and self.vel.y >= 0:
					self.pos.y = collision[0].rect.top + 1
					self.vel.y = 0
					self.jumpable = True
					self.inAir = False
				if collision[1] == 'top' and self.vel.y <= 0:
					self.pos.y = collision[0].rect.bottom + 30
					self.vel.y = 0
				if collision[1] == 'right':
					self.pos.x = collision[0].rect.left - 30
					self.vel.x = 0
				if collision[1] == 'left':
					self.pos.x = collision[0].rect.right + 1
					self.vel.x = 0

			# Deceleration
			if not self.moving and not self.inAir:
				if self.facing * self.vel.x > 0:
					self.acc.x = self.facing * -0.6
				elif self.facing * self.vel.x < 0:
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
		if self.running or self.inAir:
			if self.vel.x >= 10:
				self.vel.x = 10
			if self.vel.x <= -10:
				self.vel.x = -10
		else:
			if self.vel.x >= 4:
				self.vel.x = 4
			if self.vel.x <= -4:
				self.vel.x = -4

		# Scrolling
		if self.rect.right >= WIDTH / 3 and self.vel.x >= 0:
			self.scroll = True
			for plat in platforms:
				plat.rect.x -= abs(self.vel.x)
				if plat.rect.right <= 0:
					plat.kill()

		if self.moving and not self.inAir:
			self.movingFrames += 1
		else:
			self.movingFrames = 0

		frameDiff = 5
		
		if not self.inAir:
			if self.movingFrames == 0:
				self.sprite = "stand"
			elif self.movingFrames > 0 and self.movingFrames <= frameDiff:
				self.sprite = "walk0"
			elif self.movingFrames > frameDiff and self.movingFrames <= 2 * frameDiff:
				self.sprite = "walk1"
			elif self.movingFrames > 2 * frameDiff and self.movingFrames <= 3 * frameDiff:
				self.sprite = "walk2"
			elif self.movingFrames == 3 * frameDiff + 1:
				self.movingFrames = 0
		elif self.inAir:
			self.sprite = "jump"

		if (self.vel.x < 0 and self.acc.x > 0) or (self.vel.x > 0 and self.acc.x < 0) and not self.inAir:
			self.sprite = "skid"

		if self.dying == True:
			self.sprite = "die"

		if self.facing == 1:
			self.surf = pygame.image.load("Sprites/" + self.sprite + ".png").convert()
		else:
			self.surf = pygame.transform.flip(pygame.image.load("Sprites/" + self.sprite + ".png").convert(), True, False)

		# Update actual position of the sprite
		self.rect.bottomleft = self.pos

	def jump(self):
		if self.jumpable:
			self.vel.y = -15.5

	def checkDamage(self):
		if self.rect.top > HEIGHT and not self.dying:
			self.deathAnim()

	def deathAnim(self):
		self.vel = vec(0, -18)
		self.acc = vec(0, 0.5)
		self.dying = True
 
class platform(pygame.sprite.Sprite):
	def __init__(self, x, y, sprite):
		super().__init__()
		self.x = x
		self.y = y
		self.sprite = sprite

		self.surf = pygame.image.load("Sprites/" + self.sprite + ".png").convert()
		self.surf.set_colorkey((255, 255, 255), RLEACCEL)
		self.rect = self.surf.get_rect(center = (x, y))

P1 = Player()

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)

platforms = pygame.sprite.Group()

for i in range(0, 150):
	for k in range(0, 2):
		floor = platform(SIDE*i, HEIGHT - SIDE/2 - SIDE*k, "block")
		platforms.add(floor)
		all_sprites.add(floor)

for x in range(0, 20):
	pl = platform(SIDE * random.randint(3, 125), HEIGHT - SIDE/2 - SIDE * 2, "brick")
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

'''
--BUGS--
	- Left and right collision doesn't function
	- Platforms going offscreen during scrolling go slower at the border for some reason
	- Clipping into platforms for 1 frame every time theres collision
'''
