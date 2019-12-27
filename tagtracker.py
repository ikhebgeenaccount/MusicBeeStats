class TagTracker:
	"""A TagTracker tracks the stats for a type of tag. Example: TagTracker('Artist', 'Play Count') tracks the total
	play count for every unique artist encountered. The second argument can also be omitted, then the number of
	occurrences of unique tags will be counted. """

	# TODO: add a function, like TagTracker('Artist', 'Name', lambda track: track.get('name')[0] == 'a') (counts for
	#  each Artist the number of songs that start with an 'a') Where the lambda either returns True,
	#  and then occurrences are counted, or a value where occurrences of all possible values are counted,
	#  like TagTracker('Artist', 'Name', lambda track: track.get('name')[0]) (counts for each Artist the number of
	#  songs that start with a particular letter)

	# TODO: lower() all the tags so differently capitalized artists will be tracked together

	def __init__(self, tag=None, tag_data=None, unique=True, func=None):
		self.tag = tag
		self.tag_data = tag_data
		self.data = {}
		self.unique = unique

		if self.tag_data:
			self.func = lambda item: item.get(self.tag_data)
			self.default_func = True
		elif self.tag:
			self.func = lambda item: item.get(self.tag)
			self.default_func = True

		if func:
			self.func = func
			self.default_func = (tag is None)

	# TODO: clean code so new arguments for init don't add n^2 new if statements
	def evaluate(self, track):
		"""Evaluates the given Track for the sought after tag. If the tag is found, and there is data in tag_data,
		it is added to the tracker. """
		if self.tag_data or not self.default_func:
			# If the track has the tag that we are tracking and it has the relevant data, add it
			if not track.get(self.tag)is None and not self.func(track) is None:
				# Check if this is a new tag we track
				if track.get(self.tag) in self.data.keys():
					# If not, add up if it's a number, otherwise append to list
					if not self.unique and isinstance(self.func(track), int):
						self.data[track.get(self.tag)] += self.func(track)
					else:
						self.data[track.get(self.tag)].append(self.func(track))
				else:
					# It's a new tag, add as a new number or list
					if not self.unique and isinstance(self.func(track), int):
						self.data[track.get(self.tag)] = self.func(track)
					else:
						self.data[track.get(self.tag)] = [self.func(track)]
		else:
			if not self.func(track)is None:
				if self.func(track) in self.data.keys():
					if not self.unique and isinstance(self.func(track), int):
						self.data[self.func(track)] += self.func(track)
					else:
						self.data[self.func(track)] += 1
				else:
					if not self.unique and isinstance(self.func(track), int):
						self.data[self.func(track)] = self.func(track)
					else:
						self.data[self.func(track)] = 1
