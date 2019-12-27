class TagTracker:
	"""A TagTracker tracks the stats for a type of tag. Example: TagTracker('Artist', 'Play Count') tracks the total
	play count for every unique artist encountered. The second argument can also be omitted, then the number of
	occurrences of unique tags will be counted. """

	def __init__(self, tag=None, tag_data=None, unique=True, func=None, case_sensitive=False):
		self.tag = tag
		self.tag_data = tag_data
		self.data = {}
		self.case_map = {}
		self.unique = unique
		self.case_sensitive = case_sensitive

		if self.tag_data:
			self.func = lambda item: item.get(self.tag_data)
			self.default_func = True
		elif self.tag:
			self.func = lambda item: item.get(self.tag)
			self.default_func = True

		if func:
			self.func = func
			self.default_func = (tag is None)

	def evaluate(self, track):
		"""Evaluates the given Track for the sought after tag. If the tag is found, and there is data in tag_data,
		it is added to the tracker. """
		value = self.func(track)
		if self.tag_data or not self.default_func:
			# If the track has the tag that we are tracking and it has the relevant data, add it
			key = track.get(self.tag)

			if key is not None and value is not None:  # is not None because if value returns False for value = 0
				if not self.case_sensitive and isinstance(key, str) and key.lower() in self.case_map.keys():
					key = self.case_map[key.lower()]
				elif isinstance(key, str):
					self.case_map[key.lower()] = key

				# Check if this is a new tag we track
				if key in self.data.keys():
					# If not, add up if it's a number, otherwise append to list
					if not self.unique and isinstance(value, int):
						self.data[key] += value
					else:
						self.data[key].append(value)
				else:
					# It's a new tag, add as a new number or list
					if not self.unique and isinstance(value, int):
						self.data[key] = value
					else:
						self.data[key] = [value]
		else:
			if value is not None:
				if not self.case_sensitive and isinstance(value, str) and value.lower() in self.case_map.keys():
					value = self.case_map[value.lower()]
				elif isinstance(value, str):
					self.case_map[value.lower()] = value

				if value in self.data.keys():
					if not self.unique and isinstance(value, int):
						self.data[value] += value
					else:
						self.data[value] += 1
				else:
					if not self.unique and isinstance(value, int):
						self.data[value] = value
					else:
						self.data[value] = 1
