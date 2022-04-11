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
GRAV = 0.7
SIDE = 32
 
FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.sprite = "stand"
		self.state = "small"

		self.surf = pygame.image.load("Sprites/" + self.sprite + "_" + self.state + ".png").convert()
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
		self.crouching = False

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
			if pressed_keys[K_LSHIFT] and not self.crouching:
				if pressed_keys[K_RIGHT]:
					self.facing = 1
					self.run()
				elif pressed_keys[K_LEFT]:
					self.facing = -1
					self.run()
			elif not pressed_keys[K_LSHIFT] and not self.crouching:
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
					if collision[0].sprite == "question" or collision[0].sprite == "brick":
						collision[0].opening = True
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
			self.vel.x = 0

		# Speed cap
		if self.running or (self.inAir and self.running):
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
		if self.rect.right >= WIDTH / 2.5 and self.vel.x >= 0:
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

		if ((self.vel.x < 0 and self.acc.x > 0) or (self.vel.x > 0 and self.acc.x < 0)) and not self.inAir:
			self.sprite = "skid"

		if not self.inAir and pressed_keys[K_DOWN] and self.state == "big":
			self.sprite = "crouch"
			self.crouching = True
		else:
			self.crouching = False

		if self.dying == True:
			self.sprite = "die"

		if self.facing == 1:
			self.surf = pygame.image.load("Sprites/" + self.sprite + "_" + self.state + ".png").convert()
		else:
			self.surf = pygame.transform.flip(pygame.image.load("Sprites/" + self.sprite + "_" + self.state + ".png").convert(), True, False)

		self.rect = self.surf.get_rect()

		# Update actual position of the sprite
		self.rect.bottomleft = self.pos

	def jump(self):
		if self.jumpable:
			self.vel.y = -14 - abs(self.vel.x + 0.01)/3

	def checkDamage(self):
		if self.rect.top > HEIGHT and not self.dying:
			self.state = "small"
			self.deathAnim()

	def deathAnim(self):
		self.vel = vec(0, -16)
		self.acc = vec(0, 0.6)
		self.dying = True
 
class platform(pygame.sprite.Sprite):
	def __init__(self, x, y, sprite):
		super().__init__()
		self.sprite = sprite
		self.x = SIDE/2 + SIDE * x
		self.y = HEIGHT - SIDE/2 - SIDE * y
		self.opening = False

		self.surf = pygame.image.load("Sprites/" + self.sprite + ".png").convert()
		self.surf.set_colorkey((255, 255, 255), RLEACCEL)
		self.rect = self.surf.get_rect(center = (self.x, self.y))

		self.pos = vec(0, 0)
		self.pos.x = self.x
		self.pos.y = self.y
		self.vel = vec(0,0)

	def open(self):
		if self.sprite == "question":
			if self.vel.y <= 0:
				self.vel.y = -5
				self.pos.y += self.vel.y
			if self.pos.y <= self.y - 25 or self.vel.y > 0:
				self.vel.y = 5
				self.pos.y += self.vel.y
				if self.pos.y >= self.y:
					self.vel.y = 0
					self.pos.y = self.y
					self.opening = False
					self.sprite = "empty-question"
		if self.sprite == "brick":
			self.kill()

	def update(self):
		if self.opening:
			self.open()

		self.rect.bottom = self.pos.y + SIDE/2
		self.surf = pygame.image.load("Sprites/" + self.sprite + ".png").convert()

P1 = Player()

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)

platforms = pygame.sprite.Group()

for i in range(0, 150):
	for k in range(0, 2):
		floor = platform(i, k, "ground")
		platforms.add(floor)
		all_sprites.add(floor)

blocks = [
platform(10, 4, "question"),
platform(13, 4, "brick"),
platform(14, 4, "question"),
platform(15, 4, "brick"),
platform(16, 4, "question"),
platform(17, 4, "brick"),
platform(15, 7, "question"),

]

for block in blocks:
	platforms.add(block)
	all_sprites.add(block)

while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				P1.jump()
	 
	displaysurface.fill((41, 200, 214))
 
	P1.update()
	for platform in platforms:
		if platform.opening:
			platform.update()

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
