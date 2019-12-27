import json

TAGS = ['Track ID', 'Name', 'Artist', 'Album', 'Genre', 'Year', 'Size', 'Total Time', 'Date Added', 'Play Count', 'Play Date UTC', 'Persistent ID']
TAG_NAMES = ['track_id', 'name', 'artist', 'album', 'genre', 'year', 'size', 'total_time', 'date_added', 'play_count', 'play_date', 'location']


class Track:
	"""Track is a data storage class for all data regarding a single track."""

	def __init__(self, track_id=-1, name=None, artist=None, album=None, genre=None, year=0, size=0, total_time=0, date_added=None, play_count=0, play_date=None, location=None):
		"""Initializes a Track object with specified data."""
		self.data = {
			'track_id': int(track_id),
			'name': name,
			'artist': artist,
			'album': album,
			'genre': genre,
			'year': year,
			'size': int(size),
			'total_time': int(total_time),
			'date_added': date_added,
			'play_count': int(play_count),
			'play_date': play_date,
			'location': location
		}

	def get(self, identifier_string):
		if identifier_string in TAG_NAMES:
			return self.data[identifier_string]
		return None

	# Comparison functions
	def __eq__(self, other):
		return self.get('track_id') == other.get('track_id')

	# Comparison of play counts
	def __ne__(self, other):
		return self.data['play_count'] != other.data['play_count']

	def __lt__(self, other):
		return self.data['play_count'] < other.data['play_count']

	def __le__(self, other):
		return self.data['play_count'] <= other.data['play_count']

	def __gt__(self, other):
		return self.data['play_count'] > other.data['play_count']

	def __ge__(self, other):
		return self.data['play_count'] >= other.data['play_count']

	# to String
	def __str__(self):
		return json.dumps(self.data)

	# Addition functions
	def __add__(self, other):
		return Track(play_count=self.data['play_count'] + other.data['play_count'], size=self.data['size'] + other.data['size'], total_time=self.data['total_time'] + other.data['total_time'])

	def __radd__(self, other):
		if other == 0:
			return Track(play_count=self.data['play_count'], size=self.data['size'], total_time=self.data['total_time'])
		return self.__add__(other)

	# Subtraction functions
	def __sub__(self, other):
		return Track(play_count=self.data['play_count'] - other.data['play_count'], size=self.data['size'] - other.data['size'], total_time=self.data['total_time'] - other.data['total_time'])

	def __rsub__(self, other):
		if other == 0:
			return Track(play_count=self.data['play_count'], size=self.data['size'], total_time=self.data['total_time'])
		return self.__add__(other)
