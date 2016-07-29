#!/usr/bin/python
# Ben Chapman-Kish
# 2016-07-28
# Crowdface pong: 2-side pong game controlled by a crowd of people changing the angle of their heads

import sys, os, math, time, random, pygame

class Paddle(object):
	def __init__(self, game, team, pos, size, col):
		self.team = team
		self.rect = pygame.Rect(pos, size)
		self.game = game
		
	def draw(self):
		pygame.draw.rect(self.game.screen, self.col, self.rect)
	
class Ball(object):
	def __init__(self, game, pos, vel, rad, col):
		self.pos = pos
		self.vel = vel
		self.rad = rad
		self.col = col
		self.inplay = True
		self.game = game
		
	def draw(self):
		pygame.draw.circle(self.game.screen, self.col, map(int, self.pos), self.rad)
		
	def move(self):
		self.pos[0] += self.vel[0]
		self.pos[1] += self.vel[1]
		for x in (0, 1):
			if (self.pos[x] > self.game.size[x] and self.vel[x] > 0) or (self.pos[x] < 0 and self.vel[x] < 0):
				self.vel[x] *= -1
		for p in self.game.paddles:
			if self.pos
			
class Game(object):
	def __init__(self, size):
		pygame.init()
		pygame.display.set_caption('Crowdface Pong')
		self.size = size
		self.screen = pygame.display.set_mode(self.size)
		self.clock = pygame.time.Clock()
		self.FPS = 60
		self.running = True
		self.balls = []
		self.paddles = []
	
	def newBall(self, pos, vel = None, rad = 25, col = pygame.Color("white")):
		if not vel:
			nb = random.randrange(2) * 2 - 1 # Random value of either -1 or 1
			vel = [nb * random.random.randint(10, 20), random.randint(-20, 20)] # Ensure X velocity won't be close to 0
		self.balls.append(Ball(self, map(float, pos), map(float, vel), rad, col))
	
	def newPaddle(self, team, pos, size = (50, 250), col = pygame.Color("white")):
		self.paddles.append(Paddle(self, team, map(float, pos), size, col))
		
	def eventLoop(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.KEYDOWN:
				if event.key = pygame.K_ESCAPE:
					self.running = False
	
	def update(self):
		
	
	def render(self):
		self.screen.draw()
		for p in self.paddles:
			p.draw()
		for b in self.balls:
			if b.inplay:
				b.draw()
		pygame.display.update()
	
	def mainLoop(self):
		self.eventLoop()
		self.update()
		self.render()
		self.clock.tick(self.FPS)
	
Game((1280, 800)).mainLoop()
pygame.quit()
