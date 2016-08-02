#!/usr/bin/python
# Ben Chapman-Kish
# 2016-07-28
# Crowdface pong: 2-side pong game controlled by a crowd of people changing the angle of their heads

import sys, os, math, time, random, pygame

class Paddle(object):
	def __init__(self, game, team, pos, size, col):
		self.team = team
		self.dir = 0
		self.moverate = 5.0
		self.rect = pygame.Rect(pos, size)
		self.col = col
		self.game = game

	def move(self):
		self.rect.centery = max(0, min(self.rect.centery - self.dir * self.moverate, self.game.size[1]))
		
	def draw(self):
		pygame.draw.rect(self.game.screen, self.col, self.rect)
	
class Ball(object):
	def __init__(self, game, pos, vel, rad, col):
		self.pos = pos
		self.vel = vel
		self.rad = rad
		self.ocol = col # Original color
		self.col = col
		self.inplay = True
		self.game = game
		
	def move(self):
		self.pos[0] += self.vel[0]
		self.pos[1] += self.vel[1]
		if (self.pos[1] + self.rad > self.game.size[1] and self.vel[1] > 0) or (self.pos[1] - self.rad < 0 and self.vel[1] < 0):
			self.vel[1] *= -1
		if self.pos[0] + self.rad > self.game.size[0]:
			self.game.scores[1] += 1
			self.reset()
		else if self.pos[0] - self.rad < 0:
			self.game.scores[0] += 1
			self.reset()
		#for p in self.game.paddles:
		#	if self.pos

	def reset(self):
		self.inplay = False
		self.pos = map(lambda x: x/2.0, self.game.size)
		self.col = self.col[:3] + (self.col[3] / 2,)
		self.game.newTimer(3000, self.enterPlay, self)
	
	def enterPlay(self)
		self.col = self.ocol
		self.inplay = True
			
	def draw(self):
		pygame.draw.circle(self.game.screen, self.col, map(int, self.pos), self.rad)
			
class Game(object):
	def __init__(self, size):
		pygame.init()
		pygame.display.set_caption('Crowdface Pong')
		self.size = size
		self.screen = pygame.display.set_mode(self.size)
		self.clock = pygame.time.Clock()
		self.FPS = 60
		self.bgcolor = pygame.Color("black")
		self.running = True
		self.timers = []
		self.scores = [0, 0]
		self.balls = []
		self.paddles = []
		
		self.newPaddle(0, 100)
		self.newBall()
	
	def newBall(self, pos = None, vel = None, rad = 25, col = pygame.Color("white")):
		if not pos:
			pos = map(lambda x: x / 2.0, self.size)
		if not vel:
			nb = random.randrange(2) * 2 - 1 # Random value of either -1 or 1
			vel = [nb * random.randint(100, 200) / 10.0, random.randint(-200, 200) / 10.0]
			# Initialize a random velocity, where the X velocity won't be close to 0 and the values are floats
		self.balls.append(Ball(self, pos, vel, rad, col))
	
	def newPaddle(self, team, pos, size = (50, 250), col = pygame.Color("white")):
		if isinstance(pos, (int, long, float)):
			pos = [pos, self.size[1] / 2.0]
		self.paddles.append(Paddle(self, team, pos, size, col))
	
	def newTimer(self, delay, func, args = ()):
		self.timers.append((pygame.time.get_ticks(), delay, func, args))
		
	def eventLoop(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.running = False
				elif event.key == pygame.K_UP:
					self.paddles[0].dir = 1
				elif event.key == pygame.K_DOWN:
					self.paddles[0].dir = -1
					
			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_UP:
					self.paddles[0].dir = 0
				elif event.key == pygame.K_DOWN:
					self.paddles[0].dir = 0
	
	def update(self):
		for p in self.paddles:
			p.move()
		for b in self.balls:
			if b.inplay:
				b.move()
	
	def timerCheck(self):
		newtimers = []
		for time, func, args in self.timers:
			if time <= pygame.time.get_ticks():
				func(*args)
			else:
				newtimers.append((time, func, args))
		self.timers = newtimers
	
	def render(self):
		self.screen.fill(self.bgcolor)
		for p in self.paddles:
			p.draw()
		for b in self.balls:
			b.draw()
		pygame.display.flip()
	
	def mainLoop(self):
		while self.running:
			self.eventLoop()
			self.update()
			self.render()
			self.clock.tick(self.FPS)
	
Game((1080, 720)).mainLoop()
pygame.quit()
