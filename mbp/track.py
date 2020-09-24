import json
import re

TAGS = ['Track ID', 'Name', 'Artist', 'Album', 'Genre', 'Year', 'Size', 'Total Time', 'Date Added', 'Play Count', 'Play Date UTC', 'Location', 'Bit Rate']
TAG_NAMES = ['track_id', 'name', 'artist', 'album', 'genre', 'year', 'size', 'total_time', 'date_added', 'play_count', 'play_date', 'location', 'bitrate']


def encode_track(track):
	return (track.get('name') if track.get('name') else '') \
		+ (track.get('artist') if track.get('artist') else '') \
		+ (track.get('album') if track.get('album') else '') \
		# + (str(track.get('size')) if track.get('size') else '')


class Track:
	"""Track is a data storage class for all data regarding a single track."""

	def __init__(self, track_id=-1, name=None, artist=None, album=None, genre=None, year=0, size=0, total_time=0, date_added=None, play_count=0, play_date=None, location=None, bitrate=0):
		"""Initializes a Track object with specified data."""
		if isinstance(year, str):
			# If year is a string, take the first occurrence of 4 consecutive numbers as the year
			match = re.search('[0-9]{4}', year)
			if match:
				year = year[match.start():match.end()]
			else:
				year = 0

		self.data = {
			'track_id': int(track_id),
			'name': name,
			'artist': artist,
			'album': album,
			'genre': genre,
			'year': int(year),
			'size': int(size),
			'total_time': int(total_time),
			'date_added': date_added,
			'play_count': int(play_count),
			'play_date': play_date,
			'location': location,
			'bitrate': int(bitrate)
		}

	def get(self, identifier_string):
		if identifier_string in TAG_NAMES:
			return self.data[identifier_string]
		return None

	# # Comparison functions
	# def __eq__(self, other):
	# 	return self.get('track_id') == other.get('track_id')
	#
	# # Comparison of play counts
	# def __ne__(self, other):
	# 	return self.data['play_count'] != other.data['play_count']
	#
	# def __lt__(self, other):
	# 	return self.data['play_count'] < other.data['play_count']
	#
	# def __le__(self, other):
	# 	return self.data['play_count'] <= other.data['play_count']
	#
	# def __gt__(self, other):
	# 	return self.data['play_count'] > other.data['play_count']
	#
	# def __ge__(self, other):
	# 	return self.data['play_count'] >= other.data['play_count']

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

	# Equality operator
	def __eq__(self, other):
		threshold = 0.8
		if isinstance(other, Track):
			checks = []
			for t in TAG_NAMES:
				if self.get(t) and other.get(t) and t not in ['play_count', 'play_date']:
					checks.append(self.get(t) == other.get(t))

			return sum(checks) / len(checks) >= threshold
		else:
			return False

	def __hash__(self):
		return hash((self.get('name'), self.get('artist'), self.get('album')))
