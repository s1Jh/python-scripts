import os
import re

"""
    Custom json-like definition file format parser.
"""

BACKWARDS = 0
FORWARDS = 1


class Reader:
	def __init__(self, file=None, aliases=None):
		self.dir = ""
		self.suppressed = False
		if aliases is None:
			self.aliases = {}
		else:
			self.aliases = aliases
		if file is not None:
			self.set_file(file)
		else:
			self.file = None

	def add_alias(self, name, replacement):
		self.aliases[name] = replacement

	def toggle_mute(self):
		if self.suppressed:
			self.suppressed = False
		else:
			self.suppressed = True

	def visualize(self, target=None, tree=None):
		vis = ""
		if tree is None:
			t = self.read()
		else:
			t = tree

		del tree

		def iterate(group: dict, level: int):
			vis = ""
			keys = list(group.keys())
			for key in keys:
				if type(group[key]) is bool:
					vis += f"{level * '│'}{'└' if key == keys[-1] else '├'}{key}\n"
				elif type(group[key]) is dict:
					vis += f"{level * '│'}{'└' if key == keys[-1] else '├'}{key}\n"
					vis += iterate(group[key], level + 1)
				else:
					vis += f"{level * '│'}{'└' if key == keys[-1] else '├'}{key} = {group[key]}\n"
			return vis

		vis = iterate(t, 0)

		if target is None:
			print(vis)
		else:
			target = vis
		return True

	def remove_alias(self, name):
		if name in self.aliases:
			del self.aliases[name]
			return True
		return False

	def set_file(self, new_file):
		self.dir = new_file
		if os.path.isfile(new_file):
			if not self.suppressed:
				print(f"[READER] File set: {new_file}")
			file_obj = open(self.dir, 'r')
			self.file = file_obj.read()
			file_obj.close()
			return True
		else:
			if not self.suppressed:
				print(f"[READER] File not found: {new_file}")
			self.file = ""
			return False

	def read(self):
		structure = {}
		for alias in self.aliases.keys():
			self.file = self.file.replace(f"%{alias}%", self.aliases[alias])

		def get_token(text: str, mode=FORWARDS):
			matches = re.findall("\"(.*?)\"", text)
			#print(f"matches: {matches}")
			if len(matches) > 0:
				if mode == FORWARDS:
					return matches[0].replace("\"", "")
				else:
					return matches.pop().replace("\"", "")
			return ""

		def get_clump(search_chunk, parent):
			i = 0

			while i < len(search_chunk):
				if search_chunk[i] == '$':
					tag_name = get_token(search_chunk[i:], mode=FORWARDS)
					parent[tag_name] = True
					#print(f"Found tag {tag_name}")
				elif search_chunk[i] == '=':
					tag_end = search_chunk[i:].find("\n")
					val = get_token(search_chunk[i:], mode=FORWARDS)
					key = get_token(search_chunk[:i], mode=BACKWARDS)
					if key not in parent:
						parent[key] = val
					else:
						l = [val, parent[key]]
						parent[key] = l
					#print(f"Found tag {key} : {val}")
				elif search_chunk[i] == '{':
					# find the clump name
					name = get_token(search_chunk[:i], mode=BACKWARDS)
					if name not in parent:
						parent[name] = {}
					else:
						l = [{}, parent[name]]
						parent[name] = l
					#print(f"Found clump {name}")
					# right now we're at a "{" symbol so we need to start the next search clump at the next char
					next_start = i + 1
					# left and right bracket counters
					lb = 0
					rb = 0
					for search in range(i, len(search_chunk)):
						if search_chunk[search] == '{':
							lb += 1
						elif search_chunk[search] == '}':
							rb += 1
						if lb == rb:
							i = search
							break
					if lb != rb:
						if not self.suppressed:
							print(f"[READER]: brace miscount found in file {self.dir}, clump {name}")
					get_clump(search_chunk[next_start:i], parent[name])
					# we should end at a "{" character which is technically okay since we don't look for these
					# but it's just another wasted cycle so we offset it and start at the next char
					i += 1
				i += 1

		get_clump(self.file, structure)
		#print(f"Read structure {structure}")
		return structure
