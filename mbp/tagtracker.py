class TagTracker:
	"""A TagTracker tracks a certain tag.
	Arguments:
	tag - the tag to be tracked, can be either a str or a function which takes a Track and outputs some value
	tag_data - the data tag to be tracked grouped under tag, can be either a str or a function which takes a Track and outputs some value
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
	TagTracker('artist', tag_data=lambda t: t.get('play_count') * t.get('total_time'), unique=False)

	Counts the number of songs that start with a particular letter:
	TagTracker(tag=lambda t: t.get('name')[0])
	"""
	def __init__(self, tag, tag_data=None, unique=True, case_sensitive=False):
		if isinstance(tag, str):
			self.tag = lambda t: t.get(tag)
		else:
			self.tag = tag

		if isinstance(tag_data, str):
			self.tag_data = lambda t: t.get(tag_data)
		else:
			self.tag_data = tag_data

		self.data = {}
		self.case_map = {}
		self.unique = unique
		self.case_sensitive = case_sensitive

	def evaluate(self, track):
		"""Evaluates the given Track for the sought after tag. If the tag is found, and there is data in tag_data,
		it is added to the tracker. """
		if self.tag_data:
			# If the track has the tag that we are tracking and it has the relevant data, add it
			key = self.tag(track)
			value = self.tag_data(track)

			if key is not None and value is not None:  # is not None because if value returns False for value = 0
				if not self.case_sensitive and isinstance(key, str) and key.lower() in self.case_map.keys():
					key = self.case_map[key.lower()]
				elif not self.case_sensitive and isinstance(key, str):
					self.case_map[key.lower()] = key

				# Check if this is a new tag we track
				if key in self.data.keys():
					# If not, add up if it's a number, otherwise append to list
					if not self.unique and (isinstance(value, int) or isinstance(value, float)):
						self.data[key] += value
					else:
						self.data[key].append(value)
				else:
					# It's a new tag, add as a new number or list
					if not self.unique and (isinstance(value, int) or isinstance(value, float)):
						self.data[key] = value
					else:
						self.data[key] = [value]
		else:
			value = self.tag(track)
			if value is not None:
				if not self.case_sensitive and isinstance(value, str) and value.lower() in self.case_map.keys():
					value = self.case_map[value.lower()]
				elif not self.case_sensitive and isinstance(value, str):
					self.case_map[value.lower()] = value

				if value in self.data.keys():
					if not self.unique and (isinstance(value, int) or isinstance(value, float)):
						self.data[value] += value
					else:
						self.data[value] += 1
				else:
					if not self.unique and (isinstance(value, int) or isinstance(value, float)):
						self.data[value] = value
					else:
						self.data[value] = 1

	# TODO: add arithmetic functions

	def __sub__(self, other):
		new_data = {}

		# Subtract related entries
		for i in self.data:
			new_data[i] = self.data[i] - other.data[i] if i in other.data else self.data[i]

		# Add -count for every entry not in self.data
		for i in other.data:
			if i not in self.data:
				new_data[i] = -1 * other.data[i]

		ret_tt = TagTracker(self.tag, self.tag_data, self.unique, self.case_sensitive)
		ret_tt.data = new_data
		return ret_tt

	def __rsub__(self, other):
		return self.return_self()

	def __add__(self, other):
		pass

	def __radd__(self, other):
		return self.return_self()

	def __div__(self, other):
		pass

	def __rdiv__(self, other):
		return self.return_self()

	def __mul__(self, other):
		pass

	def __rmul__(self, other):
		return self.return_self()

	def return_self(self):
		r = TagTracker(self.tag, self.tag_data, self.unique, self.case_sensitive)
		r.data = self.data
		return r
