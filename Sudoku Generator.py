import pygame
import itertools
import random

# os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()

game_exit = False

mouse_1 = False
mouse_1_states = []  # Tracks what state mouse_1 was in in the previous loop
should_promote = False
promotion_states = []  # Tracks which frame a pawn was placed in the last file
cell_gap_y = 40
cell_gap_x = cell_gap_y

sqrs_in_line = 9  # How many squares in a row or column

# Colours

off_white = (230, 230, 230)
white = (255, 255, 255)
black = (0, 0, 0)
grey = (60, 60, 60)
light_grey = (135, 135, 135)
red = (245, 0, 0)
green = (0, 215, 0)
blue = (0, 0, 245)
purple = (150, 0, 175)
pink = (245, 105, 180)
turquoise = (0, 206, 209)
ochre = (204, 119, 34)
brown = (155, 83, 19)
light_brown = (255, 218, 185)

display_width = 800
display_height = 600
resolution = (display_width, display_height)

Display = pygame.display.set_mode(resolution)

pygame.display.set_caption('Chess')

clock = pygame.time.Clock()

# Fonts
small_font_size = display_width // 25
med_font_size = display_width // 12
large_font_size = display_width // 5

small_font = pygame.font.SysFont('Roboto', small_font_size)
med_font = pygame.font.SysFont('Roboto', med_font_size)
large_font = pygame.font.SysFont('Roboto', large_font_size)

# Images
img_width = 68
mini_img_width = 51

loc_squares = {}
hover_loc = None
clicked_piece = None
clicked_cell = None

available_movement_wait = False  # This is to make the function available_movement wait a frame before activating


class Cell:
	def __init__(self,
	             colour=black,
	             top_left=((display_width / 4) + 15, 15),
	             width_height=(3 * display_width / 100, 3 * display_height / 100),
	             number=1,
	             thickness=1,
	             highlight=False,
	             highlight_thickness=3):
		self.colour = colour
		self._x1 = top_left[0]
		self._y1 = top_left[1]
		self.width = width_height[0]
		self.height = width_height[1]
		self.x2 = self._x1 + self.width
		self.y2 = self._y1 + self.height
		self.number = number
		self.thickness = thickness
		self.highlight = highlight
		self.was_highlighted = False  # Keeps track of the last highlighted cell
		self.high_thick = highlight_thickness
		self.show = True
		self.loc = None

	@property
	def x1(self):
		return self._x1

	@property
	def y1(self):
		return self._y1

	@x1.setter
	def x1(self, value):
		self._x1 = value
		self.x2 = value + self.width

	@y1.setter
	def y1(self, value):
		self._y1 = value
		self.y2 = value + self.height

	def draw_to_screen(self):
		if not self.highlight:
			Display.fill(black, rect=[self.x1,
			                          self.y1,
			                          self.width,
			                          self.height])

			Display.fill(self.colour, rect=[self.x1 + self.thickness,
			                                self.y1 + self.thickness,
			                                self.width - 2 * self.thickness,
			                                self.height - 2 * self.thickness])

		if self.show:
			message_to_screen(str(self.number), black, x_displace=self.x1 + self.width / 2,
			                  y_displace=self.y1 + self.height / 2,
			                  side='custom_center')

	def __repr__(self):
		return self.loc


def board_coords(coords):
	"""
	input: list with 2 elements

	:param coords:
	:return:
	"""
	index_count = 0
	board_dict = {}
	for i in range(sqrs_in_line):
		non_str_num = sqrs_in_line - i
		num = str(non_str_num)
		letter_val = 97

		for v in range(sqrs_in_line):
			letter = chr(letter_val)
			key = letter + num

			board_dict[key] = coords[index_count]

			letter_val += 1
			index_count += 1

	return board_dict





def attempt_board(m=3):
	"""Make one attempt to generate a filled m**2 x m**2 Sudoku board,
	returning the board if successful, or None if not.

	"""
	n = m ** 2
	numbers = list(range(1, n + 1))
	board = [[None for _ in range(n)] for _ in range(n)]
	for i, j in itertools.product(range(n), repeat=2):
		i0, j0 = i - i % m, j - j % m  # origin of mxm block
		random.shuffle(numbers)
		for x in numbers:
			if (x not in board[i]  # row
			    and all(row[j] != x for row in board)  # column
			    and all(x not in row[j0:j0 + m]  # block
			            for row in board[i0:i])):
				board[i][j] = x
				break
		else:
			# No number is valid in this cell.
			return attempt_board(m)
	return board


def repeat(m=3):
	n = attempt_board(m)
	if n is None:
		n = repeat(m)
	return n

def from_nested(to_convert):
	"""
	merges a list of nested lists into 1 list
	:param to_convert: a list of nested lists
	:return:
	"""

	merged = list(itertools.chain.from_iterable(to_convert))

	return merged


sudoku_board = from_nested(repeat())

def just_board_coords():
	coord_list = []
	for i in range(sqrs_in_line):
		non_str_num = sqrs_in_line - i
		num = str(non_str_num)
		letter_val = 97

		for v in range(sqrs_in_line):
			letter = chr(letter_val)
			ans = letter + num

			coord_list.append(ans)
			letter_val += 1
	return coord_list


def generate_board():
	# Gap between edge of screen and the board:
	global cell_gap_y
	global cell_gap_x

	# Keeps track of which colour from colour list to use:
	colour_count = 0

	flip = False  # When generating the colour for the board, it flips the logic every row

	corner_rows = []
	corner_columns = []
	square_coords = []
	square_list = []

	total_width = (3 * display_width / 4) - (2 * cell_gap_x)
	total_height = display_height - (2 * cell_gap_y)  # This was display_width. Maybe change it back later

	square_width = total_width / sqrs_in_line
	square_height = total_height / sqrs_in_line

	counter = 0

	loc_list = just_board_coords()

	if square_width > square_height:
		cell_gap_x += (square_width - square_height)
		square_width = square_height
	else:
		cell_gap_y += (square_height - square_width)
		square_height = square_width
	for square_column in range(sqrs_in_line):
		corner_columns.append(square_column * square_height + cell_gap_y)
		for square_row in range(sqrs_in_line):
			x1 = square_row * square_width + cell_gap_x + display_width / 4
			y1 = square_column * square_height + cell_gap_y

			# if not (colour_count) % (sqrs_in_line ** 0.5):
			# 	x1 += 5

			corner_rows.append(x1)
			square = cells[counter]
			square.x1 = x1
			square.y1 = y1
			square.width = square_width
			square.height = square_height
			square.loc = loc_list[counter]
			square.number = sudoku_board[counter]

			space_between = 2
			if ord(square.loc[0]) > ord('c'):
				square.x1 += space_between

			if ord(square.loc[0]) > ord('f'):
				square.x1 += space_between

			if int(square.loc[1]) < 7:
				square.y1 += space_between

			if int(square.loc[1]) < 4:
				square.y1 += space_between

			if colour_count % 2 == 1:
				if flip:
					colour = white
				else:
					colour = off_white
			else:
				if flip:
					colour = off_white
				else:
					colour = white

			square.colour = colour
			square_list.append(square)
			colour_count += 1
			if not colour_count % sqrs_in_line + 1:
				flip = not flip

			centre_coordinate = [x1 + square_width / 2, y1 + square_height / 2]

			square_coords.append(centre_coordinate)

			counter += 1

	for square_index in range(len(square_list)):
		square_list[square_index].draw_to_screen()
	letter_ascii = 97
	for x in range(sqrs_in_line):
		letter = chr(letter_ascii)
		message_to_screen(letter,
		                  white,
		                  y_displace=cell_gap_y,
		                  x_displace=corner_rows[x] + square_width / 2,
		                  side='custom_bottom')
		message_to_screen(letter,
		                  white,
		                  y_displace=display_height - cell_gap_y,
		                  x_displace=corner_rows[x] + square_width / 2,
		                  side='custom_top')
		letter_ascii += 1
	num = sqrs_in_line
	for y in range(sqrs_in_line):
		message_to_screen(str(num),
		                  white,
		                  y_displace=corner_columns[y] + square_height / 2,
		                  x_displace=cell_gap_x + display_width / 4 - 5,
		                  side='custom_mid_right')
		message_to_screen(str(num),
		                  white,
		                  y_displace=corner_columns[y] + square_height / 2,
		                  x_displace=display_width - cell_gap_x + 5,
		                  side='custom_mid_left')
		num -= 1

	board_loc = board_coords(square_coords)

	return board_loc, square_list


def text_object(text, colour, size):
	if size == 'small':
		text_surface = small_font.render(text, True, colour)
	elif size == 'medium':
		text_surface = med_font.render(text, True, colour)
	else:
		text_surface = large_font.render(text, True, colour)
	return text_surface, text_surface.get_rect()


def message_to_screen(msg,
                      colour,
                      y_displace=0,
                      x_displace=0,
                      size='small',
                      side='center'):
	"""
	Each 'side' differs in their starting positions,
	point of the text box being controlled and
	in the direction of the displacements

	The name od the 'side' indicates the starting position as well as
	the point of the text box being controlled

	Center: Pygame directions
	Top: Pygame directions
	Bottom Left: Negative y
	Bottom Right: Negative y and Negative x
	:param msg:
	:param colour:
	:param y_displace:
	:param x_displace:
	:param size:
	:param side:
	:return:
	"""
	text_surf, text_rect = text_object(msg, colour, size)
	if side == 'center':
		text_rect.center = (display_width / 2) + x_displace, \
		                   (display_height / 2) + y_displace
	elif side == 'top':
		text_rect.midtop = (display_width / 2) + x_displace, y_displace
	elif side == 'bottom_left':
		text_rect.bottomleft = (x_displace,
		                        display_height - y_displace)
	elif side == 'bottom_right':
		text_rect.bottomright = (display_width - x_displace,
		                         display_height - y_displace)
	elif side == 'custom_center':
		text_rect.center = x_displace, y_displace
	elif side == 'custom_top':
		text_rect.midtop = x_displace, y_displace
	elif side == 'custom_bottom':
		text_rect.midbottom = x_displace, y_displace
	elif side == 'custom_bot_left':
		text_rect.bottomleft = x_displace, y_displace
	elif side == 'custom_bot_right':
		text_rect.bottomright = x_displace, y_displace
	elif side == 'custom_mid_right':
		text_rect.midright = x_displace, y_displace
	elif side == 'custom_mid_left':
		text_rect.midleft = x_displace, y_displace
	else:
		text_rect.center = (display_width / 2) + x_displace, \
		                   (display_height / 2) + y_displace
	Display.blit(text_surf, text_rect)


def check_hover_cell(square_list):
	pos = pygame.mouse.get_pos()
	for obj in square_list:
		if obj.x1 <= pos[0] < obj.x2 and obj.y1 <= pos[1] < obj.y2:
			return obj
	return None


def game_loop():
	global mouse_1
	global mouse_1_states
	global loc_squares
	global should_promote
	global promotion_states
	global game_exit
	global clicked_piece
	global available_movement_wait

	game_exit = False

	mouse_1 = False

	while not game_exit:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				game_exit = True
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_p:
					pass
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					mouse_1 = True
			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					mouse_1 = False

		mouse_1_states.insert(0, mouse_1)
		mouse_1_states = mouse_1_states[:15]

		promotion_states.insert(0, should_promote)
		promotion_states = promotion_states[:2]

		Display.fill(grey)

		Display.fill(ochre, rect=[0, 0, display_width / 4, display_height])

		height = img_width / 2

		Display.fill(grey, rect=[0,
		                          (display_height / 2) - height,
		                          display_width / 4,
		                          2 * height])

		# loc_squares is a dictionary of square
		# location names as the keys and the center coordinate of
		# the squares as the value eg 'a8': [272.5, 72.5]
		loc_squares, square_list = generate_board()

		# print(check_hover_cell(cells))

		pygame.display.update()
		clock.tick(60)

	pygame.quit()
	quit()


dragged_piece_loc = []

# Cells for the board

cells = []

for i in range(sqrs_in_line ** 2):
	cells.append(Cell())

for _ in range(int((9 * 9) * 0.75)):
	a = random.choice(cells)
	a.show = False

game_loop()
