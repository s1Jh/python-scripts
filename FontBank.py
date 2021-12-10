import pygame
import os

"""
    Simple class to manage pygame fonts.
    Reduces the number of rasterzation calls.
"""

class FontBank:
	def __init__(self, font_name: str, size: int, bold: bool = False, italic: bool = False):
		if os.path.isfile(font_name):
			self._font_object = pygame.font.Font(font_name, size, bold, italic)
		else:
			self._font_object = pygame.font.SysFont(font_name, size, bold, italic)

		print("Creating new FontBank for: " + font_name)

		self._letters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!?.,()"
		
		self._bank = self._font_object.render(self._letters, True, (255, 255, 255))
		
	def get_char(self, ch: chr, surf: pygame.Surface = None, invert: bool = False, oX: int = 0, oY: int = 0):
		dimensions = self._font_object.size(ch)
		# if we don't get a surf parameter, we'll create a new white surface that fits the char perfectly
		if surf is None:
			surf = pygame.Surface(dimensions)
			surf.fill((255, 255, 255))

		return_surf = pygame.Surface(dimensions)
		return_surf.blit(surf, (oX, oY))

		clip = pygame.Rect((self._letters.find(ch)*dimensions[0], 0), dimensions)

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
