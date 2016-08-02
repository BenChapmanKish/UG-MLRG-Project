#!/usr/bin/python
# Ben Chapman-Kish
# 2016-07-28
# Crowdface pong: 2-side pong game controlled by a crowd of people changing the angle of their heads

import sys, os, math, time, random, pygame

class Team(object):
	"""
	Team(TeamNumber) -> Team

	A team object currently just holds a score and controls paddles.
	"""
	def __init__(self, teamNumber):
		self.n = teamNumber
		self.score = 0
		self.paddle = None

class CenterLine(object):
	"""
	CenterLine(MainGameHandler, X-Position, DashCount, LineWidth, Color) -> CenterLine

	A dashed line that divides the game window into two areas.
	"""
	def __init__(self, game, xpos, dashes, width, col):
		self.game = game
		self.xpos = xpos
		self.w = width
		self.i = self.game.size[1] / (2.0*dashes-1)
		self.col = col
	
	def draw(self):
		"""
		draw() -> None
		"""
		y=0
		while y < self.game.size[1] + self.i:
			pygame.draw.line(self.game.screen, self.col, (self.xpos, y), (self.xpos, y+self.i), self.w)
			y += 2*self.i

class Sprite(object):
	"""
	Sprite(...) -> Sprite
	[Not yet implemented]
	"""
	def __init__(self, surface, sprite, pos, size, angle):
		self.surface = surface
		self.originalSprite = sprite
		self.pos = pos
		self.size = size
		self.angle = angle
		self.updateSprite()
	
	def updateSprite(self):
		self.sprite = pygame.transform.rotate(pygame.transform.scale(self.originalSprite, self.size), math.degrees(self.angle))
		self.rect = self.sprite.get_rect()
		self.rect.center = self.pos

	def draw(self):
		self.surface.blit(self.sprite, self.rect)

class Paddle(object):
	"""
	Paddle(MainGameHandler, TeamObject, Position, Size, MoveRate, Color) -> Paddle

	A paddle object moves up and down on the screen, serving as a means to
	bounce a all object away from the edge, so as to prevent the opposing
	team from scoring a point.

	To create a new paddle, using Game.NewPaddle is encouraged.
	"""
	def __init__(self, game, team, pos, size, moverate, col):
		self.team = team

		# The dir property is currently ternary (of values -1, 0, or 1)
		# This will be replaced once crowdface pose estimation has been integrated
		self.dir = 0

		self.moverate = moverate
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

	To create a new ball, using Game.NewBall is encouraged.
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

		# Display a 3 second countdown so the crowd knows when the ball will start moving
		self.game.newCountDown("BallStart", 3, self.enterPlay, (self.game.size[0]/2, self.game.size[1]/2 + 75))

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
		if (self.pos[1] + self.rad > self.game.size[1] and math.pi < self.angle < 2*math.pi) \
			or (self.pos[1] - self.rad < 0 and 0 < self.angle < math.pi):
			self.angle = 2*math.pi - self.angle

		# The ball hits the right side of the screen
		if self.pos[0] + self.rad > self.game.size[0]:
			self.game.teams[0].score += 1
			self.destroy(True)
			return
		
		# The ball hits the left side of the screen
		elif self.pos[0] - self.rad < 0:
			self.game.teams[1].score += 1
			self.destroy(True)
			return

		# Check the ball's position against the paddles'
		for p in self.game.paddles:
			hitXLeft  = p.rect.right > self.pos[0] - self.rad and p.rect.left  < self.pos[0]
			hitXRight = p.rect.left  < self.pos[0] + self.rad and p.rect.right > self.pos[0]
			withinY = p.rect.top < self.pos[1] + 1.5*self.rad and p.rect.bottom > self.pos[1] - 1.5*self.rad
			movingLeft = math.pi/2 < self.angle < math.pi*3/2
			movingRight = math.pi/2 < (self.angle+math.pi) % (2*math.pi) < math.pi*3/2
			
			# The ball hits a paddle
			# The ball's resultant angle is dependant on where on the paddle it hits
			if withinY:
				reflectFactor = (self.pos[1] - p.rect.centery) / (p.rect.h/2.0)
				if hitXLeft and movingLeft:
					self.angle = (-reflectFactor*math.pi/3) % (2*math.pi)
				elif hitXRight and movingRight:
					self.angle = (reflectFactor*math.pi/3 + math.pi) % (2*math.pi)

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

	To create a new Text object, using Game.NewText is encouraged.
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
	CountDown(MainGameHandler, InitialValue, EndFunction, ObjectName, CenterPosition, FontName, FontSize, AntiAlias, Color) -> CountDown

	A special Text object that counts down from a provided value until it reaches zero.
	This object recursively calls a timer on itself every second, decrementing its value each time.
	When the CountDown reaches zero, if an end function is provided, it will be executed.

	To create a new CountDown, using Game.NewCountDown is encouraged.
	"""
	def __init__(self, game, initValue, endFunc, name, centerPos, fontName, size, aa, col):
		Text.__init__(self, game, name, centerPos, fontName, size, aa, col)
		self.value = initValue
		self.endFunc = endFunc
		self.setLabel(str(self.value))
		self.game.newTimer(1000, self.decrease)
	def decrease(self):
		"""
		decrease() -> None
		Set the label of the text object to the current value, then decrement the value.
		If the value is greater than zero, set a timer to call this function again in one second,
		otherwise destroy this object.
		"""
		# This code is pretty self-explanatory
		self.value -= 1
		self.setLabel(str(self.value))
		if self.value > 0:
			self.game.newTimer(1000, self.decrease)
		else:
			if self.endFunc:
				self.endFunc()
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
		self.teams = (Team(1), Team(2))
		self.timers = []
		self.texts = []
		self.balls = []
		self.paddles = []
		self.sprites = (self.balls, self.paddles, self.texts)
		self.line = CenterLine(self, self.size[0]/2, 15, 1, (127,)*3)
		
		self.newPaddle(self.teams[0], 100)
		self.newPaddle(self.teams[1], -100)
		self.newBall()
		self.newText("Score1", (self.size[0] / 4, 70), "Monospace", 60)
		self.newText("Score2", (self.size[0]*3/4, 70), "Monospace", 60)
	
	def newBall(self, pos = None, angle = None, speed = 8, rad = 25, col = pygame.Color("white")):
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
		# If both width and height are provided, obviously use them
		# But if only one value is given, use it as height and use a default width
		if isinstance(size, (int, long, float)):
			size = (25, size)

		# If both X and Y positions are provided for position, use those
		# If only one value is given, use it for the X position and use
		# the center of the screen for the Y position
		# If the X position is negative, use it as a right-offset
		if isinstance(pos, (int, long, float)):
			if pos < 0:
				pos = self.size[0] + pos
			pos = [pos - size[0] / 2.0, self.size[1] / 2.0 - size[1] / 2.0]
		newPaddle = Paddle(self, team, pos, size, moverate, col)
		team.paddle = newPaddle
		self.paddles.append(newPaddle)
	
	def newText(self, name, pos, fontName = "Arial", size = 40, col = pygame.Color("white"), aa = True):
		"""
		newText(ObjectName, Position, FontName, FontSize, Color, AntiAlias) -> None
		"""
		self.texts.append(Text(self, name, pos, fontName, size, aa, col))
	
	def newCountDown(self, name, initValue, endFunc, pos, fontName = "Arial", size = 40, col = pygame.Color("white"), aa = True):
		"""
		newCountDown(ObjectName, InitialValue, EndFunction, Position, FontName, FontSize, Color, AntiAlias) -> None
		"""
		self.texts.append(CountDown(self, initValue, endFunc, name, pos, fontName, size, aa, col))
	
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
		Loops through the pygame events and acts accordingly.
		In the final version of this game, this will only
		wait for the signal that the game has ended.
		Currently, it also uses the keyboard to control
		the paddles, for testing purposes.
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
	
	def getCrowdPose(self):
		"""
		getCrowdPose() -> undetermined data type
		Retrieve the crowd pose. This will probably just consist of
		a forward pass through the pose estimation convnet.
		[Not yet implemented]
		"""
		return
	
	def determineTeamPose(self):
		"""
		determineTeamPose() -> None
		Use the data gathered by getCrowdPose to
		determine the average pose for each team.
		[Not yet implemented]
		"""
		pose = self.getCrowdPose()
		return
	
	def update(self):
		"""
		update() -> None
		Move all sprites that have continuous movement (i.e. balls, paddles).
		"""
		for p in self.paddles:
			p.move()
		for b in self.balls:
			if b.inplay:
				b.move()
	
	def timerCheck(self):
		"""
		timerCheck() -> None
		Check for timers that should go off, and execute their
		included function, then remove that timer from the list.
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
		Render all the visuals of the game. Begins by filling the screen's
		background, then draws all the paddles, balls, and text objects,
		followed by updating the contents of the display.
		"""
		self.screen.fill(self.bgcolor)
		self.line.draw()
		for x in self.paddles:
			x.draw()
		for x in self.balls:
			x.draw()
		self.setTextLabelByName("Score1", str(self.teams[0].score))
		self.setTextLabelByName("Score2", str(self.teams[1].score))
		for x in self.texts:
			x.draw()
		pygame.display.flip()
	
	def mainLoop(self):
		"""
		mainLoop() -> None
		Loop through the core functions of the game.
		The loop process order is as follows:
			*Loop through and react to the pygame events
			*Determine the average pose of each playing team
			*Move all sprites that have constant movement
			*Check for timers that need to go off, and for
				those that do, execute their function
			*Render all sprites
			*Tick the clock
		The loop will stop once the running property is False.
		"""
		while self.running:
			self.eventLoop()
			self.determineTeamPose()
			self.update()
			self.timerCheck()
			self.render()
			self.clock.tick(self.FPS)
	
if __name__ == "__main__":
	Game().mainLoop()
	pygame.quit()
