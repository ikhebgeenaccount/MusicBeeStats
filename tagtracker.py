class TagTracker:
	"""A TagTracker tracks a certain tag.
	Arguments:
	tag - the tag to be tracked
	tag_data - the data tag to be tracked grouped under tag
	func - a function that accepts a track and outputs some value that will be tracked
	unique - boolean, True means each instance will be tracked separately, False means that an attempt will be made to add the data up, but this will only work for int type data
	case_sensitive - boolean, whether to track differently capitalized strings together or separately

	Examples:

	Counts the number of tracks for each artist separately:
	TagTracker('artist')
	Note: it counts the number of occurrences of each separate artist, since we have a list of songs with tags artist this constitutes the number of songs of each artist in the library

	Counts the play count for each artist separately:
	TagTracker('artist', 'play_count', unique=False)
	Note: in the above example, if unique is not passed the play_counts of each song will not be summed

	Counts the play count for each genre separately:
	TagTracker('genre', 'play_count', unique=False)

	Sums the total play time of songs per artist:
	TagTracker('artist', 'total_time', unique=False)

	Calculates the total time played for each artist:
	TagTracker('artist', func=lambda t: t.get('play_count') * t.get('total_time'), unique=False)

	Counts the number of songs that start with a particular letter:
	TagTracker(func=lambda t: t.get('name')[0])
	"""

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
				elif not self.case_sensitive and isinstance(key, str):
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
				elif not self.case_sensitive and isinstance(value, str):
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
