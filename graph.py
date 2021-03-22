import pygame
import os
import math
import traceback
import configparser


"""
    Very simple unfinished but mostly functional graphing application.
"""

def func(x):
	return 2 + 3 / (-x+1)


def main():


	pygame.init()

	config = configparser.ConfigParser()
	config.read(os.path.join(os.getcwd(), "grapher_config.ini"))

	def convert(value):
		if not type(value) == str:
			r_tuple = (0, 0, 0)
			return r_tuple
	
		r_tuple = (
			int("0x" + value[0:2], 0),  # R
			int("0x" + value[2:4], 0),  # G
			int("0x" + value[4:6], 0),  # B
		)
		return r_tuple

	SCALE_VEL_INCREMENT = config.getfloat("settings", "SCALE_VEL_INCREMENT", fallback=0.01)
	SCALE_VEL_DECREMENT = config.getfloat("settings", "SCALE_VEL_INCREMENT", fallback=0.007)
	SCALE_VEL_MAX = config.getfloat("settings", "SCALE_VEL_MAX", fallback=0.1)
	SCROLLING_DAMP = config.getfloat("settings", "SCALE_VEL_MAX", fallback=2)
	SCROLLING_MULTIPLIER = config.getfloat("settings", "SCALE_VEL_MAX", fallback=0.5)
	SCALE_MIN = config.getfloat("settings", "SCALE_MIN", fallback=0.00000000001)
	COLOR_GRAPH = convert(config.get("settings", "COLOR_GRAPH", fallback="000000"))
	COLOR_BG = convert(config.get("settings", "COLOR_BG", fallback="000000"))
	COLOR_FONT = convert(config.get("settings", "COLOR_FONT", fallback="FFFFFF"))
	COLOR_LINE = convert(config.get("settings", "COLOR_FONT", fallback="FFFFFF"))
	COLOR_CURSOR = convert(config.get("settings", "COLOR_FONT", fallback="FFFFFF"))
	WINDOW_WIDTH = config.getint("settings", "WINDOW_WIDTH", fallback=1000)
	WINDOW_HEIGHT = config.getint("settings", "WINDOW_HEIGHT", fallback=1000)
	FONT = config.get("settings", "FONT", fallback="consolas")
	KEYBIND_ZOOM_IN = config.getint("settings", "KEYBIND_ZOOM_IN", fallback=33)
	KEYBIND_ZOOM_OUT = config.getint("settings", "KEYBIND_ZOOM_OUT", fallback=34)
	KEYBIND_SET_ZOOM = config.getint("settings", "KEYBIND_SET_ZOOM", fallback=35)
	TARGET_FRAMERATE = config.getint("settings", "TARGET_FRAMERATE", fallback=60)
	CALC_STRIDE = config.getint("settings", "CALC_STRIDE", fallback=1)
	CURSOR_CIRCLE_SIZE = config.getint("settings", "CURSOR_CIRCLE_SIZE", fallback=7)
	
	window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
	clock = pygame.time.Clock()
	font_30 = FontBank(FONT, 30)
	
	pygame.display.set_caption("Graph")
	
	expression = "pow(x, 2)"
	scale = 1.0
	scaling_vel = 0.0
	space = 100
	fps = 0
	collecting_input = False
	collecting_input_complete = False
	input_buffer = ""
	message_fail = font_30.get_string("Invalid Expression", invert=True)
	message_fail_syntax = font_30.get_string("Syntax Error", invert=True)
	message_invalid_points = font_30.get_string("Invalid points", invert=True)
	o_vel = [0, 0]
	oX = 0
	oY = 0
	collection_target = None

	COLOR_GRAPH = (255, 255, 255)
	COLOR_LINE = (255, 255, 255)
	COLOR_CURSOR = (255, 255, 255)

	def get_at(x):
		return scale * (x - oX - window.get_width() / 2) / space
		
	up = True
	while up:
		# ---Input Handling---
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				up = False
			elif event.type == pygame.KEYDOWN:
				if collecting_input:
					if event.unicode == '':
						input_buffer = input_buffer[0:-1]
					else:
						input_buffer += event.unicode
				elif collecting_input and event.key == pygame.K_ESC:
					collecting_input = False
					input_buffer = ""
				elif event.key == pygame.K_h and not collecting_input:
					input_buffer = ""
					collecting_input = True
					collecting_input_complete = False
				elif event.key == pygame.K_c:
					oX = 0
					oY = 0
					o_vel[0] = 0
					o_vel[1] = 0
				elif event.key == pygame.K_v:
					scale = 1
				elif collecting_input and (event.key == pygame.K_KP_ENTER or event.key == pygame.K_ENTER):
					collecting_input_complete = True
			elif event.type == pygame.MOUSEMOTION:
				if pygame.mouse.get_pressed()[2]:
					oX += event.rel[0]
					oY += event.rel[1]
					o_vel[0] = event.rel[0] * SCROLLING_MULTIPLIER
					o_vel[1] = event.rel[1] * SCROLLING_MULTIPLIER

		keys = pygame.key.get_pressed()

		if not pygame.mouse.get_pressed()[2]:
			# scrolling velocity damping
			for i in range(len(o_vel)):
				if o_vel[i] != 0:
					if o_vel[i] > 0:
						if o_vel[i] - SCROLLING_DAMP > 0:
							o_vel[i] -= SCROLLING_DAMP
						else:
							o_vel[i] = 0
					else:
						if o_vel[i] + SCROLLING_DAMP < 0:
							o_vel[i] += SCROLLING_DAMP
						else:
							o_vel[i] = 0

			# apply scrolling velocity
			oX += o_vel[0]
			oY += o_vel[1]


		# scaling handling
		if keys[pygame.K_f] and scaling_vel < SCALE_VEL_MAX:
			scaling_vel += SCALE_VEL_INCREMENT

		if keys[pygame.K_g] and abs(scaling_vel) < SCALE_VEL_MAX:
			scaling_vel -= SCALE_VEL_INCREMENT

		if not keys[pygame.K_f] and not keys[pygame.K_g]:
			if scaling_vel >= 0:
				if scaling_vel - SCALE_VEL_DECREMENT >= 0:
					scaling_vel -= SCALE_VEL_DECREMENT
				else:
					scaling_vel = 0
			else:
				if scaling_vel + SCALE_VEL_DECREMENT <= 0:
					scaling_vel += SCALE_VEL_DECREMENT
				else:
					scaling_vel = 0

		if (scale + scaling_vel) > SCALE_MIN:
			scale += scaling_vel
		else:
			scale += abs(scale + scaling_vel)

		# ---Window drawing---
		window.fill(COLOR_BG)

		# draw the two lines
		pygame.draw.line(window, COLOR_GRAPH, (window.get_width() / 2 + oX, 0),
						 (window.get_width() / 2 + oX, window.get_height()), 2)
		pygame.draw.line(window, COLOR_GRAPH, (0, window.get_height() / 2 + oY),
						 (window.get_width(), window.get_height() / 2 + oY), 2)

		# graph and number drawing
		points = []
		for pixel in range(int(window.get_width() / CALC_STRIDE) + 1):		
			x = get_at(pixel * CALC_STRIDE)
			y = 0

			try:
				y = eval(expression, {}, {"x": x})
				#y = func(x)
			except ZeroDivisionError:
				# doesn't matter in this context
				pass
			except SyntaxError:
				print(traceback.format_exc())
				window.blit(message_fail_syntax, ((window.get_width()  - message_fail_syntax.get_width() ) / 2, (window.get_height() - message_fail_syntax.get_height()) / 2))
				break
			except Exception:
				print(traceback.format_exc())
				window.blit(message_fail, ((window.get_width()  - message_fail_syntax.get_width() ) / 2, (window.get_height() - message_fail_syntax.get_height()) / 2))
				break

			# pixel coordinates
			x_pixel = math.ceil(space * x / scale) + window.get_width() / 2 + oX
			y_pixel = - math.ceil(space * y / scale) + window.get_height() / 2 + oY

			points.append((x_pixel, y_pixel))
				
		try:
			pygame.draw.lines(window, COLOR_LINE, False, points)
		except Exception:
			print("Invalid points")
			print(points)
			window.blit(message_invalid_points, ((window.get_width()  - message_invalid_points.get_width() ) / 2, (window.get_height() - message_invalid_points.get_height()) / 2))

		# draw X cursor
		frame_X = get_at(pygame.mouse.get_pos()[0])
		try:
			frame_Y = math.ceil(eval(expression, {}, {"x": x}) * 100 ) / 100
			frame_y_pixel = - math.ceil(space * frame_Y / scale) + window.get_height() / 2 + oY
			pygame.draw.circle(window, COLOR_CURSOR, [int(pygame.mouse.get_pos()[0]), int(frame_y_pixel)], CURSOR_CIRCLE_SIZE)
			frame_Y = str(frame_Y)
		except ZeroDivisionError:
			frame_Y = "∞"
		
		window.blit(font_30.get_string("At: {}".format(str(math.ceil(frame_X * 100) / 100))), (pygame.mouse.get_pos()[0] + 20, pygame.mouse.get_pos()[1]))
		window.blit(font_30.get_string("Value: {}".format(frame_Y)), (pygame.mouse.get_pos()[0] + 20, pygame.mouse.get_pos()[1] + 30))
		pygame.draw.line(window, COLOR_CURSOR, (pygame.mouse.get_pos()[0], 0), (pygame.mouse.get_pos()[0], window.get_height()), 1)

		# draw fps meter
		window.blit(font_30.get_string("@" + str(fps) + "(Target: {fps} {p}%)".format(fps=str(TARGET_FRAMERATE), p=str(
			math.ceil(fps / TARGET_FRAMERATE * 100)))), (0, 35))
			
		# draw experssion
		expr_surf = font_30.get_string(f"f(x)={expression}")
		window.blit(expr_surf, ((window.get_width() - expr_surf.get_width()) / 2, 0))

		# draw position indicator
		window.blit(font_30.get_string("Position: {}x{}".format(-oX, oY)), (0, 75))

		# draw velocity indicator (debugging only)
		window.blit(font_30.get_string("Velocity: {}".format(o_vel)), (0, 100))

		# draw scale meter or the scale input prompt
		if collecting_input:
			window.blit(font_30.get_string("Enter new scale: " + input_buffer), (0, 0))

			# this here handles text input
			if collecting_input_complete:
				collecting_input_complete = False
				collecting_input = False
				print("Done collecting input, result: " + input_buffer)
				try:
					scale = float(input_buffer)
				except ValueError:
					print("invalid value")
		else:
			window.blit(font_30.get_string("Scale: " + str(math.ceil(scale * 100) / 100)), (0, 0))

		# ---Updates---
		pygame.display.flip()
		fps = int(clock.get_fps())
		clock.tick(TARGET_FRAMERATE)
	
	pygame.quit()

class FontBank:
	def __init__(self, font_name: str, size: int, bold: bool = False, italic: bool = False):
		if os.path.isfile(font_name):
			self._font_object = pygame.font.Font(font_name, size, bold, italic)
		else:
			self._font_object = pygame.font.SysFont(font_name, size, bold, italic)

		print("Creating new FontBank for: " + font_name)

		self._letters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!?.:,()%@"

		self.render()

	def render(self, extra_letters=""):
		self._letters += extra_letters
		self._bank = self._font_object.render(self._letters, True, (255, 255, 255))

	def get_char(self, ch: chr, surf: pygame.Surface = None, invert: bool = False, oX: int = 0, oY: int = 0):
		dimensions = self._font_object.size(ch)
		# if we don't get a surf parameter, we'll create a new white surface that fits the char perfectly
		if surf is None:
			surf = pygame.Surface(dimensions)
			surf.fill((255, 255, 255))

		return_surf = pygame.Surface(dimensions)
		return_surf.blit(surf, (oX, oY))

		if self._letters.find(ch) == -1:
			self.render(ch)

		clip = pygame.Rect((self._letters.find(ch) * dimensions[0], 0), dimensions)

		# grab the mask we need
		char_mask = pygame.Surface(dimensions)
		char_mask.blit(self._bank, (0, 0), clip)

		if not invert:
			return_surf.blit(char_mask, (0, 0), None, pygame.BLEND_RGB_MULT)
		else:
			return_surf.blit(char_mask, (0, 0), None, pygame.BLEND_RGB_SUB)

		return return_surf

	def get_string(self, s: str, surf: pygame.Surface = None, invert: bool = False, oX: int = 0, oY: int = 0):
		return_surf = pygame.Surface(self._font_object.size(s))

		offset = 0
		for char in s:
			char_surf = self.get_char(char, surf, invert, oX, oY)
			return_surf.blit(char_surf, (offset, 0))
			offset += self._font_object.size(char)[0]

		return return_surf


if __name__ == '__main__':
	main()
