from pygame.locals import *
from datetime import datetime
import random
import pygame

# Direction IDs
LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3

class Food:
	x = 0
	y = 0
	rand = 0
	
	def __init__(self, is_random):
		self.rand = random.Random()
		if is_random:
			self.rand.seed(datetime.now())
		else:
			self.rand.seed(0)
		self.move()
	
	def move(self):
		self.x = self.rand.randrange(App.map_size) * App.square_size
		self.y = self.rand.randrange(App.map_size) * App.square_size

class Player:
	x = 0
	y = 0
	dir = RIGHT
	tail = [[0,0]]
	tail_end = 0
	
	def __init__(self):
		self.x = App.square_size
		self.y = 0
		tail = [[0,0]]
		tail_end = 0
	
	def move(self, new_dir):
		old_x = self.x
		old_y = self.y
		invalid_move = 0
		
		if new_dir < 0 or new_dir > 3:
			if App.verbose: print("INVALID DIRECTION: " + str(new_dir))
			return False
		
		# Move head
		if new_dir == UP:
			new_head = [self.x, self.y - App.square_size]
			if self.dir == DOWN: return 1
			elif self.y == 0: return 2
			elif new_head in self.tail: return 3
			else: self.moveUp()
		elif new_dir == DOWN:
			new_head = [self.x, self.y + App.square_size]
			if self.dir == UP: return 1
			elif self.y >= (App.map_size - 1) * App.square_size: return 2
			elif new_head in self.tail: return 3
			else: self.moveDown()
		elif new_dir == LEFT:
			new_head = [self.x - App.square_size, self.y]
			if self.dir == RIGHT: return 1
			elif self.x == 0: return 2
			elif new_head in self.tail: return 3
			else: self.moveLeft()
		elif new_dir == RIGHT:
			new_head = [self.x + App.square_size, self.y]
			if self.dir == LEFT: return 1
			elif self.x >= (App.map_size - 1) * App.square_size: return 2
			elif new_head in self.tail: return 3
			else: self.moveRight()
			
		# Move tail
		self.tail[self.tail_end][0] = old_x
		self.tail[self.tail_end][1] = old_y
		self.tail_end = (self.tail_end + 1) % len(self.tail)
		return 4

	def moveRight(self):
		self.x = self.x + App.square_size
		self.dir = RIGHT

	def moveLeft(self):
		self.x = self.x - App.square_size
		self.dir = LEFT

	def moveUp(self):
		self.y = self.y - App.square_size
		self.dir = UP

	def moveDown(self):
		self.y = self.y + App.square_size
		self.dir = DOWN

class App:
	# Clock Speeds
	VERY_SLOW = 1000
	SLOW = 500
	NORMAL = 250
	FAST = 125
	VERY_FAST = 50
	WARP = 25
	NO_CLOCK = 0
	
	clock = NORMAL
	square_size = 20
	map_size = 10
	windowWidth = map_size * square_size
	windowHeight = map_size * square_size
	player = 0
	verbose = True

	def __init__(self):
		self._running = True
		self._display_surf = None
		self._image_head = None
		self._image_tail = None
		self._image_food = None
		self.player = Player()
		self.random_food = True
		self.moves = 0
		self.score = 0
		self.verbose = True

	def on_init(self):
		if self.clock != 0:
			pygame.init()
			self._display_surf = pygame.display.set_mode((self.windowWidth,self.windowHeight), pygame.HWSURFACE)
			
			pygame.display.set_caption('Snake')
			self._running = True
			self._image_head = pygame.image.load("head.png").convert()
			self._image_tail = pygame.image.load("tail.png").convert()
			self._image_food = pygame.image.load("food.png").convert()
 
	def on_event(self, event):
		if event.type == QUIT:
			self._running = False
	
	def on_render(self):
		if self.clock != 0:
			self._display_surf.fill((255,255,255))
			self._display_surf.blit(self._image_head,(self.player.x, self.player.y))
			for i in range(0, len(self.player.tail)):
				self._display_surf.blit(self._image_tail,(self.player.tail[i][0], self.player.tail[i][1]))
			self._display_surf.blit(self._image_food,(self.food.x, self.food.y))
			pygame.display.flip()
		
	def on_loop(self):
		pass
 
	def on_cleanup(self, result):
		# pygame.quit()
		self.reset()
		self._running = False
		print(result)
		
	def reset(self, ret_code, result = ""):
		ret = [ret_code, self.score, self.moves]
		self.score = 0
		self.moves = 0
		self._running = False
		self.player = Player()
		self.food = Food(self.random_food)
		if result != "" and self.verbose == True: print(result)
		if self.wait_on_end: pygame.time.wait(1500)
		return ret
		
	# Starts the game. Useful for playing using the step() function
	def start (
		self,
		clock = NORMAL,
		map_size = 10,
		square_size = 20,
		random_food = True,
		end_on_collisions = True,
		wait_on_end = True,
		verbose = True
	):
		self.clock = clock
		self.map_size = map_size
		self.square_size = square_size
		self.random_food = random_food
		self.end_on_collisions = end_on_collisions
		self.wait_on_end = wait_on_end
		self.verbose = verbose
		
		self.food = Food(random_food)
		self.on_init()
		
	def step (
		self,
		action
	):		
		# ==============
		# Perform action
		# ==============
		
		invalid_move = self.player.move(action)
		self.moves += 1
		
		# =================================
		# Check collisions / end conditions
		# =================================
		
		# Invalid action
		if invalid_move == 1 and self.verbose:
			print("INVALID MOVE")
		
		# Wall collision
		if invalid_move == 2 and self.end_on_collisions:
			return self.reset(-3, "WALL COLLISION")
		
		# Tail collision
		player_pos = [self.player.x, self.player.y]
		if invalid_move == 3 and self.end_on_collisions:
			return self.reset(-3, "SELF COLLISION")
			
		# No possible moves / snake is stuck
		square_L = self.player.x == 0 or \
			[self.player.x - self.square_size, self.player.y] in self.player.tail
		square_R = self.player.x == (self.map_size - 1) * self.square_size or \
			[self.player.x + self.square_size, self.player.y] in self.player.tail
		square_U = self.player.y == 0 or \
			[self.player.x, self.player.y - self.square_size] in self.player.tail
		square_D = self.player.y == (self.map_size - 1) * self.square_size or \
			[self.player.x, self.player.y + self.square_size]
		if (square_L and square_R and square_U and square_D):
			return self.reset(-4, "PLAYER STUCK")
		
		# Food collision
		food_pos = [self.food.x, self.food.y]
		if player_pos == food_pos:
			self.eat_food()
		
		# Check if Escape pressed
		if self.clock != 0:
			pygame.event.pump()
			keys = pygame.key.get_pressed() 
			if (keys[K_ESCAPE]): return self.reset(-1, "ESCAPE PRESSED")
			
		# Check if player won
		if len(self.player.tail) == self.map_size * self.map_size - 1:
			return self.reset(0, "SUCCESS!")
			
		# ============
		# Advance game
		# ============
			
		# Update screen
		self.on_render()
		
		# Wait (unless move did nothing)
		if invalid_move != 0: pygame.time.wait(self.clock)
		
		# Out of moves
		return [-2, self.score, self.moves];
	
	# Run the game as normal, with inputted actions
	def run (
		self,
		actions,
		clock = NORMAL,
		map_size = 10,
		square_size = 20,
		random_food = True,
		end_on_collisions = True,
		wait_on_end = True,
		verbose = True
	):
		self.start(clock, map_size, square_size, random_food, end_on_collisions, wait_on_end, verbose)
		
		if clock != 0:
			pygame.event.pump()
			self.on_render()
			pygame.time.wait(clock)
		
		ret = 0
		for i in range(0, len(actions)):
			ret = self.step(actions[i])
			if ret != 0: return ret
		
		# Out of moves
		return self.reset(-2, "OUT OF MOVES")
	
	def eat_food(self):
		self.score += 1
		self.food.move()
		self.player.tail.append(self.player.tail[0].copy())
		# Repeat this line for additional length from food
		#self.player.tail.append(self.player.tail[0].copy())
		#self.player.tail.append(self.player.tail[0].copy())
		
	#
	# Useful functions for learning
	#
	
	def manhattan_distance(self):
		return abs(self.player.x - self.food.x) + abs(self.player.y - self.food.y)