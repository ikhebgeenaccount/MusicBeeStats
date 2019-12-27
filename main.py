import datetime
import glob
import json
import os
import sys

import matplotlib.pyplot as plt

from musicbeelibrary import MBLibrary
from plots import barh_plot
from tagtracker import TagTracker
from track import Track


# Has some predefined plots and stuff, shows lifetime stats as well
def show_stats(file_path):
	print('MusicBee Stats')
	print('Reading library file at "' + file_path + '"')
	mbl = MBLibrary(file_path, tagtrackers=[
		# Counts the play count for each artist separately
		TagTracker('artist', 'play_count', unique=False),
		# Counts the play count for each genre separately
		TagTracker('genre', 'play_count', unique=False),
		# Counts the number of tracks for each artist separately
		TagTracker('artist'),
		# Counts the number of tracks for each genre separately
		TagTracker('genre'),
		# Counts the number of tracks released per year
		TagTracker('year'),
		# Sums the total play time of songs per artist
		TagTracker('artist', 'total_time', unique=False),
		# Calculates the total time played for each artist
		TagTracker('artist', func=lambda t: t.get('play_count') * t.get('total_time'), unique=False),
		# Counts the number of songs that start with a particular letter
		TagTracker(func=lambda t: t.get('name')[0]),
		# Calculates the total size played for each artist
		TagTracker('artist', func=lambda t: t.get('play_count') * t.get('size'), unique=False),
		# Counts the total play count per release year
		TagTracker('year', 'play_count', unique=False),
		])

	print(('{:20}{}\n' * 4 + '{:20}{:.1f}h\n' * 2 + '{} {}, {} times for a total of {:.1f} hours')
			.format('Tracks found:', len(mbl.tracks),
					'Artists found:', len(mbl.tagtrackers[2].data),
					'File size:', str(round(sum(mbl.tracks).get('size')/(1024**3), 1)) + 'GB',
					'Total play count:', sum(mbl.tracks).get('play_count'),
					'Total time:', sum(mbl.tracks).get('total_time')/3600000,
					'Total time played:', sum([track.get('play_count') * track.get('total_time') for track in mbl.tracks])/3600000,
					'Most played:', max(mbl.tracks).get('name'), max(mbl.tracks).get('play_count'), max(mbl.tracks).get('total_time') * max(mbl.tracks).get('play_count')/3600000))

	sorted_artists_by_play_count = {artist: play_count for artist, play_count in sorted(mbl.tagtrackers[0].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_genres_by_play_count = {genre: play_count for genre, play_count in sorted(mbl.tagtrackers[1].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_artists_by_play_count_over_number_of_tracks = {artist: play_count / mbl.tagtrackers[2].data[artist] for artist, play_count in sorted(filter(lambda elem: mbl.tagtrackers[2].data[elem[0]] > 10, mbl.tagtrackers[0].data.items()), key=lambda item: item[1] / mbl.tagtrackers[2].data[item[0]], reverse=True)}
	sorted_artists_by_play_time = {artist: play_time/3600000 for artist, play_time in sorted(mbl.tagtrackers[6].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_first_letter_song_name = {letter: count for letter, count in sorted(mbl.tagtrackers[7].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_artists_by_play_size = {artist: size/(1024**2) for artist, size in sorted(mbl.tagtrackers[8].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_year_by_play_count = {str(year): play_count for year, play_count in sorted(mbl.tagtrackers[9].data.items(), key=lambda item: item[1], reverse=True)}

	barh_plot(sorted_artists_by_play_count_over_number_of_tracks, 'Average play count per song per artist', 'Play count')
	barh_plot(sorted_genres_by_play_count, 'Total play count by genre', 'Play count')
	barh_plot({artist: total_time / 60000 for artist, total_time in sorted(mbl.tagtrackers[5].data.items(), key=lambda item: item[1], reverse=True)}, 'Total time (min) by artist')
	barh_plot(sorted_artists_by_play_count, 'Play count per artist', 'Play count')
	barh_plot(sorted_artists_by_play_time, 'Play time per artist', 'Play time (h)')
	barh_plot(sorted_first_letter_song_name, 'Count of songs starting with letter')
	barh_plot(sorted_artists_by_play_size, 'Play size per artist', 'Play size (mb)')
	barh_plot(sorted_year_by_play_count, 'Play count by year', 'Play count')
	# Show all created plots
	plt.show()


# Reads an 'iTunes Music Library.xml' file, with optional tagtrackers
def read_library_xml(file_path, tagtrackers=None):
	return MBLibrary(file_path, tagtrackers=tagtrackers)


# Reads an .mbl file
def read_mbl(file_path):
	tracks = []
	with open(file_path, 'r', encoding='utf-8') as mbl_file:
		for line in mbl_file:
			track_json = json.loads(line)
			tracks.append(Track(**track_json))

	return MBLibrary(tracks=tracks)


# Saves the library stats to a datestamped mbl file in the libs folder
def save_library(mblibrary):
	if not os.path.exists('libs/'):
		os.makedirs('libs/')

	dt = datetime.datetime.now()
	today = '{:0>4}{:0>2}{:0>2}'.format(str(dt.year), str(dt.month), str(dt.day))
	lib_name = 'libs/{:0>4}{:0>2}{:0>2}.mbl'.format(str(dt.year), str(dt.month), str(dt.day))

	# Check if today's date is in the list of files, if so don't save anything
	for file in glob.glob('libs/*.mbl'):
		if today in file:
			return

	# Write the library to file
	with open(lib_name, 'w', encoding='utf-8') as mbl_file:
		for track in mblibrary.tracks:
			mbl_file.write(str(track) + '\n')


# Shows stats about the difference of play counts between the new library object and the old
def show_stats_over_time(date_new, new_mbl, date_old, old_mbl):
	subbed_mbl = new_mbl - old_mbl
	sorted_subbed = sorted(subbed_mbl.tracks, key=lambda item: item.get('play_count'), reverse=True)

	tag_mbl = MBLibrary(tracks=subbed_mbl.tracks, tagtrackers=[
		TagTracker('artist', 'play_count', unique=False),
		TagTracker('artist', func=lambda item: item.get('play_count') * item.get('total_time'), unique=False)
	])

	sorted_artist_play_count = sorted(tag_mbl.tagtrackers[0].data.items(), key=lambda item: item[1], reverse=True)

	print('Over the last {} days you have added {} new songs and you listened to:'.format((date_new - date_old).days, len(new_mbl.tracks) - len(old_mbl.tracks)))

	# Print top 5 most listened to artists
	artists_base = '{:>2}. {:28}{:>5}{:>8.1f}h\n'
	artists_final = ''
	for i in range(0, 5):
		artists_final += artists_base.format(i+1, sorted_artist_play_count[i][0], sorted_artist_play_count[i][1], tag_mbl.tagtrackers[1].data[sorted_artist_play_count[i][0]]/3600000)

	print('Artists:')
	print(artists_final)

	# Print top 5 most listened to songs
	songs_base = '{:>2}. {:28.28}{:>5}\n'
	songs_final = ''
	for i in range(0, 10):
		songs_final += songs_base.format(i+1, sorted_subbed[i].get('name'), sorted_subbed[i].get('play_count'))

	print('Songs:')
	print(songs_final)

	# Print total stats
	print('All combined this makes for:\n'
			' {} total play count\n'
			' {:.1f}h total hours listened'
			.format(str(sum(tag_mbl.tracks).get('play_count')),
				sum([track.get('play_count') * track.get('total_time') for track in tag_mbl.tracks]) / 3600000))

	print('\nPress enter to close this overview')
	input()


# Finds the closest older .mbl file to given date
# It keeps expanding the windows for which it will accept a date, so if there is only today's mbl file and you're
# looking for one, in the end it'll return today's mbl file
def find_closest_mbl(date):
	found = False

	# Forward slash because glob returns the path with \\ not with /
	files = glob.glob('libs/*.mbl')
	diff = 0

	while not found:
		# Check the target date with + diff and - diff because either side of the date works
		# If we find a date that has an mbl file we return the MBLibrary and the date of that MBLibrary

		target_date = datetime.date(date.year, date.month, date.day) - datetime.timedelta(days=diff)
		target_file = 'libs\\{:0>4}{:0>2}{:0>2}.mbl'.format(target_date.year, target_date.month, target_date.day)

		if target_file in files:
			return read_mbl(target_file), target_date

		target_date = datetime.date(date.year, date.month, date.day) + datetime.timedelta(days=diff)
		target_file = 'libs\\{:0>4}{:0>2}{:0>2}.mbl'.format(target_date.year, target_date.month, target_date.day)

		if target_file in files:
			return read_mbl(target_file), target_date

		diff += 1


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('Use this program as follows: python main.py PATH_TO_FILE [-saveOnly]')
		sys.exit()

	file_path = sys.argv[1]

	if len(sys.argv) > 1 and '-saveOnly' in sys.argv:
		# User only wants to save the stats, not show any graphs and shit
		new_mbl = read_library_xml(file_path)
		save_library(new_mbl)

		today = datetime.date.today()

		# Check for first of the month or new year for stats
		if today.day == 1 and today.month == 1:
			# Print yearly stats
			old_mbl, date_old = find_closest_mbl(datetime.date(today.year - 1, 12, today.day))
			show_stats_over_time(today, new_mbl, date_old, old_mbl)
		if today.day == 1:
			# Print monthly stats
			old_mbl, date_old = find_closest_mbl(datetime.date(today.year, today.month - 1, today.day))
			show_stats_over_time(today, new_mbl, date_old, old_mbl)
	else:
		# User wants to see some interesting stuff
		show_stats(file_path)
