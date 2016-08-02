#!/usr/bin/python
# Ben Chapman-Kish
# 2016-07-28
# Crowdface pong: 2-side pong game controlled by a crowd of people changing the angle of their heads

import sys, os, math, time, random, pygame

class Paddle(object):
	"""
	Paddle(MainGameHandler, Team, Position, Size, MoveRate, Color) -> Paddle

	A paddle object moves up and down on the screen, serving as a means to
	bounce a all object away from the edge, so as to prevent the opposing
	team from scoring a point.
	"""
	def __init__(self, game, team, pos, size, moverate, col):
		# Team variable not currently in use, but I'm future-proofing
		self.team = team

		# The dir property is currently ternary (of values -1, 0, or 1)
		# This will be replaced once crowdface pose estimation has been integrated
		self.dir = 0

		self.moverate = MovementSpeed
		self.rect = pygame.Rect(pos, size)
		self.col = col
		self.game = game

	def move(self):
		"""
		move() -> None
		Move the paddle according to its direction and moverate properties.
		The paddle cannot move so that more than half of it is off the screen.
		"""
		# An easy one-liner :)
		self.rect.centery = max(0, min(self.rect.centery - self.dir * self.moverate, self.game.size[1]))
		
	def draw(self):
		"""
		draw() -> None
		Draw the paddle on the game window.
		"""
		pygame.draw.rect(self.game.screen, self.col, self.rect)
	
class Ball(object):
	"""
	Ball(MainGameHandler, Position, Angle, Speed, Radius, Color) -> Ball

	A ball object moves around the screen, bouncing on the top and bottom,
	bounces off paddle objects, and subtracts points from respective teams
	when it reaches a vertical edge of the screen.
	
	The ball will remain stationary for the first 3 seconds after it spawns,
	allowing the players to position their paddle in advance. A line to indicate
	the ball's speed and direction will appear as well, and a countdown
	will indicate how many seconds remain until the ball enters play.
	"""
	def __init__(self, game, pos, angle, speed, rad, col):
		self.pos = pos
		self.angle = angle
		self.speed = speed
		self.rad = rad
		self.ocol = col # Original color
		# Start with dimmed colors so it's obvious that it's not in play yet
		self.col = map(lambda x: x/2, self.ocol)
		self.inplay = False
		self.game = game

		# Temporary unoptimized solution for finding the line coordinates:
		offsetx = math.cos(self.angle) * self.rad * 1.2
		offsety = math.sin(self.angle) * self.rad * 1.2
		distx = math.cos(self.angle) * self.speed * 5
		disty = math.sin(self.angle) * self.speed * 5
		line0 = [self.pos[0] + offsetx, self.pos[1] - offsety]
		line1 = [self.pos[0] + offsetx + distx, self.pos[1] - offsety - disty]
		# A line to indicate the speed and direction of the ball before it starts moving
		self.line = ((line0, line1))

		# Display a visual countdown so the crowd knows when the ball will start moving
		self.game.newCountDown("BallStart", 3, (self.game.size[0]/2, self.game.size[0]/2 - 100))
		# 3 second delay before the ball starts moving so the crowd can position their paddle
		self.game.newTimer(3000, self.enterPlay)

	def enterPlay(self):
		"""
		enterPlay() -> None
		Configures the ball to enter gameplay.
		This function may also be used as a timer callback,
		allowing the ball enters play after a delayed time period.
		"""
		self.col = self.ocol
		self.line = None
		self.inplay = True
		
	def move(self):
		"""
		move() -> None
		Moves the ball according to its angle and speed properties.

		If the ball hits a horizontal edge of the window, its angle is horizontally reflected.
		If the ball hits a vertical edge of the window, it awards the appropriate team
		with a point, destroys itself, and calls for a replacement ball to spawn.

		If the ball hits a paddle, its angle is reflected and normalized according to its distance
		from the center of the paddle (for details, refer to the functionality of classic pong paddles).
		"""
		# Mod the angle
		self.angle %= 2*math.pi
		# Update the position
		self.pos[0] += math.cos(self.angle) * self.speed
		self.pos[1] -= math.sin(self.angle) * self.speed
		# Bounce off the top and bottom of the window
		if (self.pos[1] + self.rad > self.game.size[1] and math.pi < self.angle < 2*math.pi) or (self.pos[1] - self.rad < 0 and 0 < self.angle < math.pi):
			self.angle = 2*math.pi - self.angle

		# The ball hits the right side of the screen
		if self.pos[0] + self.rad > self.game.size[0]:
			self.game.scores[0] += 1
			self.destroy(True)
			return
		
		# The ball hits the left side of the screen
		elif self.pos[0] - self.rad < 0:
			self.game.scores[1] += 1
			self.destroy(True)
			return

		#for p in self.game.paddles:
		#	if self.pos
	
	def destroy(self, replace = False):
		"""
		destroy(replace=False) -> None
		Destroy this ball object, and optionally call for a replacement ball to spawn.
		"""
		if replace:
			self.game.newBall()
		self.game.balls.remove(self)
			
	def draw(self):
		"""
		draw() -> None
		Draw the ball on the game window, and if there's
		a direction/speed line, draw it as well.
		"""
		pygame.draw.circle(self.game.screen, self.col, map(int, self.pos), self.rad)
		if self.line:
			pygame.draw.line(self.game.screen, self.col, map(int, self.line[0]), map(int, self.line[1]), 2)

class Text(object):
	"""
	Text(MainGameHandler, ObjectName, CenterPosition, FontName, FontSize, AntiAlias, Color) -> Text
	
	A text object provides a convenience for text labels to render onscreen.
	The text object is given a name (that should be unique) to refer to it later.
	The label is automatically centered on the position provided, but can
	be changed later. The label's text can only be set after initialization.
	"""
	# Couldn't inherit from pygame.font because of reasons
	def __init__(self, game, name, centerPos, fontName, size, aa, col):
		self.name = name
		self.font = pygame.font.SysFont(fontName, size)
		self.centerPos = centerPos
		self.col = col
		self.aa = aa
		self.game = game
		self.labelText = None
		self.label = None
		self.renderPos = None
	def setLabel(self, text):
		"""
		setLabel(labelText) -> None
		Set the label for the text object and re-adjust the position
		to keep the label centered on the position already provided.
		"""
		self.labelText = text
		self.label = self.font.render(self.labelText, self.aa, self.col)
		textSize = self.font.size(self.labelText)
		self.renderPos = [self.centerPos[x] - textSize[x]/2 for x in (0, 1)]
	def setCenterPos(self, pos):
		"""
		setCenterPos(centerPos) -> None
		Set the position for the label to be centered on.
		"""
		self.centerPos = pos
		if self.label:
			# Just calling this so the code doesn't need to be copied here again
			self.setLabel(self.labelText)
	def draw(self):
		"""
		draw() -> None
		Blit the text on the game window.
		"""
		# This function is called draw() rather than blit() for uniformity.
		self.game.screen.blit(self.label, self.renderPos)

class CountDown(Text):
	"""
	CountDown(MainGameHandler, InitialValue, ObjectName, CenterPosition, FontName, FontSize, AntiAlias, Color) -> CountDown

	A special Text object that counts down from a provided value until it reaches zero.
	This object recursively calls a timer on itself every second, decrementing its value each time.
	"""
	def __init__(self, game, initValue, name, centerPos, fontName, size, aa, col):
		Text.__init__(self, game, name, centerPos, fontName, size, aa, col)
		self.value = initValue
		self.decrease()
	def decrease(self):
		"""
		decrease() -> None
		Set the label of the text object to the current value, then decrement the value.
		If the value is greater than zero, set a timer to call this function again in one second,
		otherwise destroy this object.
		"""
		# This code is pretty self-explanitory
		self.setLabel(str(self.value))
		if self.value > 1:
			self.value -= 1
			self.game.newTimer(1000, self.decrease)
		else:
			self.game.texts.remove(self)
	
class Game(object):
	"""
	Game(WindowSize, WindowTitle, BackgroundColor, FPS) -> Game

	The core game object that handles everything for the game.

	[Further information on this class is not currently available]
	"""
	def __init__(self, size = (1080, 720), caption = "Crowdface Pong", bgcolor = pygame.Color("black"), FPS = 60):
		pygame.init()
		pygame.display.set_caption(caption)

		self.size = size
		self.screen = pygame.display.set_mode(self.size)
		self.FPS = FPS
		self.bgcolor = bgcolor

		self.clock = pygame.time.Clock()
		self.running = True
		self.scores = [0, 0]
		self.timers = []
		self.texts = []
		self.balls = []
		self.paddles = []
		
		self.newPaddle(0, 100)
		self.newPaddle(1, -100)
		self.newBall()
		self.newText("Scores", (self.size[0]/2, 70))
	
	def newBall(self, pos = None, angle = None, speed = 10, rad = 25, col = pygame.Color("white")):
		"""
		newBall(Position, Angle, Speed, Radius, Color) -> None
		"""
		# If no position is given, use the center of the screen
		if not pos:
			pos = map(lambda x: x / 2.0, self.size)
		# If no angle is given, pick a random angle between -60 and 60 degrees
		# or between 120 and 240 degrees (so the ball has a significant X velocity)
		if not angle:
			angle = random.choice((random.randint(120, 240), random.randint(-60, 60)))
			angle = math.radians(angle % 360)
		self.balls.append(Ball(self, pos, angle, speed, rad, col))
	
	def newPaddle(self, team, pos, size = (25, 230), moverate = 7.0, col = pygame.Color("white")):
		"""
		newPaddle(Team, Position, Size, MoveRate, Color) -> None
		"""
		# If both X and Y positions are provided for position, use those
		# If only one value is given, use it for the X position and use
		# the center of the screen for the Y position
		# If the X position is negative, use it as a right-offset
		if isinstance(pos, (int, long, float)):
			if pos < 0:
				pos = self.size[0] + pos
			pos = [pos, self.size[1] / 2.0 - size[1] / 2.0]
		# As with position, if both width and height are provided, use them
		# If only one value is given, use it as height and use a default width
		if isinstance(size, (int, long, float)):
			size = (25, size)
		self.paddles.append(Paddle(self, team, pos, size, moverate, col))
	
	def newText(self, name, pos, fontName = "Arial", size = 40, col = pygame.Color("white"), aa = True):
		"""
		newText(ObjectName, Position, FontName, FontSize, Color, AntiAlias) -> None
		"""
		self.texts.append(Text(self, name, pos, fontName, size, aa, col))
	
	def newCountDown(self, name, initValue, pos, fontName = "Arial", size = 40, col = pygame.Color("white"), aa = True):
		"""
		newCountDown(ObjectName, InitialValue, Position, FontName, FontSize, Color, AntiAlias) -> None
		"""
		self.texts.append(CountDown(self, initValue, name, pos, fontName, size, aa, col))
	
	def setTextLabelByName(self, name, text):
		"""
		setTextLabelByName(ObjectName, TextLabel) -> None
		"""
		for x in self.texts:
			if x.name == name:
				x.setLabel(text)

	def setTextPosByName(self, name, pos):
		"""
		setTextPosByName(ObjectName, TextLabel) -> None
		"""
		for x in self.texts:
			if x.name == name:
				x.setCenterPos(pos)
	
	def newTimer(self, delay, func, args = ()):
		"""
		newTimer(Delay, Function, *Arguments) -> None
		"""
		self.timers.append((pygame.time.get_ticks() + delay, func, args))
	
	def eventLoop(self):
		"""
		eventLoop() -> None
		"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.running = False
				elif event.key == pygame.K_UP:
					self.paddles[1].dir = 1
				elif event.key == pygame.K_DOWN:
					self.paddles[1].dir = -1
				elif event.key == pygame.K_w:
					self.paddles[0].dir = 1
				elif event.key == pygame.K_s:
					self.paddles[0].dir = -1
					
			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_UP:
					self.paddles[1].dir = 0
				elif event.key == pygame.K_DOWN:
					self.paddles[1].dir = 0
				elif event.key == pygame.K_w:
					self.paddles[0].dir = 0
				elif event.key == pygame.K_s:
					self.paddles[0].dir = 0
	
	def update(self):
		"""
		update() -> None
		"""
		for p in self.paddles:
			p.move()
		for b in self.balls:
			if b.inplay:
				b.move()
	
	def timerCheck(self):
		"""
		timerCheck() -> None
		"""
		i=0
		while i < len(self.timers):
			time, func, args = self.timers[i]
			if time <= pygame.time.get_ticks():
				func(*args)
				self.timers.pop(i)
			else:
				i+=1
	
	def render(self):
		"""
		render() -> None
		"""
		self.screen.fill(self.bgcolor)
		for x in self.paddles:
			x.draw()
		for x in self.balls:
			x.draw()
		self.setTextLabelByName("Scores", "Score: {} - {}".format(*self.scores))
		for x in self.texts:
			x.draw()
		pygame.display.flip()
	
	def mainLoop(self):
		"""
		mainLoop() -> None
		"""
		while self.running:
			self.eventLoop()
			self.update()
			self.timerCheck()
			self.render()
			self.clock.tick(self.FPS)
	
Game().mainLoop()
pygame.quit()
