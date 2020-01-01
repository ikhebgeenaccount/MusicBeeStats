import xml.etree.ElementTree as ET
from mbp import track
from mbp.track import Track


class MBLibrary:
	"""MBLibrary handles MusicBee's iTunes XML Library file."""

	def __init__(self, file_path="", tracks=None, tagtrackers=None):
		"""Initializes an MBLibrary object. Reads the file at file_path and stores all tracks found in a list of Tracks."""
		if not tagtrackers:
			self.tagtrackers = []
		else:
			self.tagtrackers = tagtrackers

		# If tracks are passed, throw them through tagtrackers and return
		if tracks:
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

	# Arithmetic functions only subtract and add play counts of same tracks
	# Assumptions: self.tracks > other.tracks and equal track_id means same song
	# So (new library stats) - (old library stats) will work as new library will at least have higher track ids than the
	# old library stats, vice versa DOES NOT WORK
	def __sub__(self, other):
		max_track_id_self = max([t.get('track_id') for t in self.tracks])
		tracks_self = [None] * (max_track_id_self + 1)
		# Add all self tracks to list
		for t in self.tracks:
			tracks_self[t.get('track_id')] = Track(**t.data)

		# Loop over other's tracks and subtract them with a None check before
		for t in other.tracks:
			# Only subtract if you find a corresponding track
			if tracks_self[t.get('track_id')]:
				tracks_self[t.get('track_id')].data['play_count'] -= t.get('play_count')

		# Remove the None entries from the resulting tracks_self
		# Create a new MBLibrary with that list of tracks
		return MBLibrary(tracks=[subbed_track for subbed_track in tracks_self if subbed_track])

	def __rsub__(self, other):
		return MBLibrary(tracks=self.tracks)