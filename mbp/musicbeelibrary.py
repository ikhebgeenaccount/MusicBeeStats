import xml.etree.ElementTree as ET
from mbp import track
from mbp.track import Track, encode_track


class MBLibrary:
	"""MBLibrary handles MusicBee's iTunes XML Library file."""

	def __init__(self, file_path="", tracks=None, tagtrackers=None):
		"""Initializes an MBLibrary object. Reads the file at file_path and stores all tracks found in a list of Tracks."""
		if not tagtrackers:
			self.tagtrackers = []
		else:
			self.tagtrackers = tagtrackers

		# If tracks are passed, throw them through tagtrackers and return
		if type(tracks) is list:
			self.tracks = tracks

			if self.tagtrackers:
				for t in tracks:
					for tagtracker in self.tagtrackers:
						tagtracker.evaluate(t)

			return

		# Else read the file path
		if not file_path:
			raise ValueError('Pass either a file path or a list of tracks.')

		tree = ET.parse(file_path)
		root = tree.getroot()

		# List to store tracks
		self.tracks = []

		add_next = False
		tag_next = ""

		# Every track
		for single_track in root[0][11]:
			data = {}

			# Loop over every tag in the track and add them to the data if we need to save it
			for child in single_track:
				text = child.text

				# Add this one if last one said so
				if add_next:
					data[track.TAG_NAMES[track.TAGS.index(tag_next)]] = text
					add_next = False

				# If this tag is a tag we need
				if text in track.TAGS:
					add_next = True
					tag_next = text

			# If we have saved any tag, add a new Track
			if any(data.values()):
				t = Track(**data)

				for tracker in self.tagtrackers:
					tracker.evaluate(t)

				self.tracks.append(t)

	def __contains__(self, item):
		if isinstance(item, Track):
			for t in self.tracks:
				if t == item:
					return True
				elif t.get('name') == item.get('name') and t.get('artist') == item.get('artist'):
					return True
		return False

	# Arithmetic functions only subtract and add play counts of same tracks
	# Assumptions: locations of music files are equal between libraries
	# If not the case, change Track.encode_track
	def __sub__(self, other):
		# TODO: rewrite with track == track (equality operator for Track) instead of encode_track
		# how to efficiently equate tracks to eachother?
		# first sort then search? delete found tracks?
		tracks_new = {}
		# Add all self tracks to dict
		for t in self.tracks:
			if t.get('play_count') > 0:
				tracks_new[encode_track(t)] = Track(**t.data)

		# Loop over other's tracks and subtract them with a None check before
		for t in other.tracks:
			try:
				if encode_track(t) in tracks_new:
					# Subtract if you find the same track in the other MBL
					tracks_new[encode_track(t)].data['play_count'] -= t.get('play_count')
					# Remove the track if the play count results to 0
					if tracks_new[encode_track(t)].data['play_count'] == 0:
						del tracks_new[encode_track(t)]
			except IndexError:
				print(t.get('track_id'), t.get('name'))

		# Create a new MBLibrary with that list of tracks
		return MBLibrary(tracks=list(tracks_new.values()))

	def __rsub__(self, other):
		return MBLibrary(tracks=self.tracks)
