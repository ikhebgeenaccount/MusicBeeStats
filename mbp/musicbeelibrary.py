import datetime
import glob
import json
import os
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


# Reads an 'iTunes Music Library.xml' file, with optional tagtrackers
def read_library_xml(file_path, tagtrackers=None):
	return MBLibrary(file_path, tagtrackers=tagtrackers)


# Reads an .mbl file
def read_mbl(file_path, tagtrackers=None):
	tracks = []
	with open(file_path, 'r', encoding='utf-8') as mbl_file:
		for line in mbl_file:
			track_json = json.loads(line)
			tracks.append(Track(**track_json))

	return MBLibrary(tracks=tracks, tagtrackers=tagtrackers)


# Saves the library stats to a datestamped mbl file in the mbls folder
def save_library(mblibrary):
	if not os.path.exists('mbls/'):
		os.makedirs('mbls/')

	dt = datetime.datetime.now()
	today = '{:0>4}{:0>2}{:0>2}'.format(str(dt.year), str(dt.month), str(dt.day))
	lib_name = 'mbls/{:0>4}{:0>2}{:0>2}.mbl'.format(str(dt.year), str(dt.month), str(dt.day))

	# Check if today's date is in the list of files, if so don't save anything
	for file in glob.glob('mbls/*.mbl'):
		if today in file:
			return

	# Write the library to file
	with open(lib_name, 'w', encoding='utf-8') as mbl_file:
		for track in mblibrary.tracks:
			mbl_file.write(str(track) + '\n')

# Finds the closest older .mbl file to given date
# It keeps expanding the windows for which it will accept a date, so if there is only today's mbl file and you're
# looking for one, in the end it'll return today's mbl file
def find_closest_mbl(date, diff_inc=1, tagtrackers=None):
	if diff_inc == 0:
		raise ValueError("diff_inc can't be zero.")

	found = False

	files = glob.glob('mbls/*.mbl')
	diff = 0

	while not found:
		# Check the target date with + diff and - diff because either side of the date works
		# If we find a date that has an mbl file we return the MBLibrary and the date of that MBLibrary

		# Backward slash because glob returns the path with \\ not with /
		# target_date = datetime.date(date.year, date.month, date.day) - datetime.timedelta(days=diff)
		# target_file = 'mbls\\{:0>4}{:0>2}{:0>2}.mbl'.format(target_date.year, target_date.month, target_date.day)
		#
		# if target_file in files:
		# 	return read_mbl(target_file), target_date

		target_date = datetime.date(date.year, date.month, date.day) + datetime.timedelta(days=diff)
		target_file = 'mbls\\{:0>4}{:0>2}{:0>2}.mbl'.format(target_date.year, target_date.month, target_date.day)

		if target_file in files:
			return read_mbl(target_file, tagtrackers=tagtrackers), target_date

		diff += diff_inc

		if diff > 365:
			raise ValueError('Cant find close mbl for date ' + date.strftime('%m/%d/%Y'))