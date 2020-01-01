import datetime
import glob
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy

from mbp.config import Config
from mbp.musicbeelibrary import MBLibrary
from mbp.plots import barh_plot, scatter_plot
from mbp.tagtracker import TagTracker
from mbp.track import Track


# TODO: analysis of the rankings in the mbr files
# TODO: analyze songs and try to make a profile for songs I like a lot?


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
		TagTracker('artist', tag_data=lambda t: t.get('play_count') * t.get('total_time'), unique=False),
		# Counts the number of songs that start with a particular letter
		TagTracker(tag=lambda t: t.get('name')[0]),
		# Calculates the total size played for each artist
		TagTracker('artist', tag_data=lambda t: t.get('play_count') * t.get('size'), unique=False),
		# Counts the total play count per release year
		TagTracker('year', 'play_count', unique=False),
		# Counts the number of tracks in every duration with intervals of 30s
		TagTracker(tag=lambda t: int(t.get('total_time')/1000 - (t.get('total_time')/1000) % 30)),
		# Sums the play count for each interval of 30s of length of songs
		TagTracker(tag=lambda t: int(t.get('total_time')/1000 - (t.get('total_time')/1000) % 30), tag_data='play_count', unique=False),
		# Counts the number of songs of artists that start with the same letter as the artists' names
		TagTracker(tag='artist', tag_data=lambda t:t.get('artist')[0] == t.get('name')[0], unique=False),
		# Tracks the length of songs for each name length
		TagTracker(tag=lambda t:len(t.get('name')), tag_data=lambda t:t.get('total_time')),
		# Tracks the total time and size per bitrate
		TagTracker(tag='bitrate', tag_data=lambda t: [t.get('total_time'), t.get('size')]),

		# Counts the play count per album
		TagTracker(tag='album', tag_data='play_count', unique=False),
		# Sums the total time listened to per album
		TagTracker(tag='album', tag_data=lambda t: t.get('play_count') * t.get('total_time'), unique=False),
		])

	print(('{:20}{}\n' * 4 + '{:20}{:.1f}h\n' * 2 + '{} {}, {} times for a total of {:.1f} hours')
			.format('Tracks found:', len(mbl.tracks),
					'Artists found:', len(mbl.tagtrackers[2].data),
					'File size:', str(round(sum(mbl.tracks).get('size')/(1024**3), 1)) + 'GB',
					'Total play count:', sum(mbl.tracks).get('play_count'),
					'Total time:', sum(mbl.tracks).get('total_time')/3600000,
					'Total time played:', sum([track.get('play_count') * track.get('total_time') for track in mbl.tracks])/3600000,
					'Most played:', max(mbl.tracks).get('name'), max(mbl.tracks).get('play_count'), max(mbl.tracks).get('total_time') * max(mbl.tracks).get('play_count')/3600000))

	# print(mbl.tagtrackers[-1].data)

	sorted_artists_by_play_count = {artist: play_count for artist, play_count in sorted(mbl.tagtrackers[0].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_genres_by_play_count = {genre: play_count for genre, play_count in sorted(mbl.tagtrackers[1].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_artists_by_play_count_over_number_of_tracks = {artist: play_count / mbl.tagtrackers[2].data[artist] for artist, play_count in sorted(filter(lambda elem: mbl.tagtrackers[2].data[elem[0]] > 10, mbl.tagtrackers[0].data.items()), key=lambda item: item[1] / mbl.tagtrackers[2].data[item[0]], reverse=True)}
	sorted_artists_by_play_time = {artist: play_time/3600000 for artist, play_time in sorted(mbl.tagtrackers[6].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_first_letter_song_name = {letter: count for letter, count in sorted(mbl.tagtrackers[7].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_artists_by_play_size = {artist: size/(1024**2) for artist, size in sorted(mbl.tagtrackers[8].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_year_by_play_count = {str(year): play_count for year, play_count in sorted(mbl.tagtrackers[9].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_tracks_by_length = {'{} - {}'.format(base, base + 30): count for base, count in sorted(mbl.tagtrackers[10].data.items(), key=lambda item: item[0])}
	sorted_tracks_play_count_by_length = {'{} - {}'.format(base, base + 30): count for base, count in sorted(mbl.tagtrackers[11].data.items(), key=lambda item: item[0])}
	sorted_artist_song_first_letter = {artist: count for artist, count in sorted(mbl.tagtrackers[12].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_album_by_play_count = {album: play_count for album, play_count in sorted(mbl.tagtrackers[15].data.items(), key=lambda item: item[1], reverse=True) if play_count > 500}
	sorted_album_by_play_time = {album: round(play_time/3600000, 0) for album, play_time in sorted(mbl.tagtrackers[16].data.items(), key=lambda item: item[1], reverse=True) if play_time > 24 * 3600000}

	scatter_name_time_length = []
	for key in mbl.tagtrackers[13].data.keys():
		for val in mbl.tagtrackers[13].data[key]:
			scatter_name_time_length.append([key, val/1000])

	total_size_length_by_bitrate = mbl.tagtrackers[14].data

	groups = list(total_size_length_by_bitrate.keys())
	x_data = []
	y_data = []
	c = 0
	for arr in total_size_length_by_bitrate.values():
		x_data.append([])
		y_data.append([])
		counter = 1
		for sub_arr in arr:
			for value in sub_arr:
				if counter % 2 == 0:
					y_data[c].append(round(value/(1024**2), 2))
				else:
					x_data[c].append(round(value/1000, 2))
				counter += 1
		c += 1

	x_data = numpy.asarray(x_data)
	y_data = numpy.asarray(y_data)

	color = numpy.asarray([tuple(numpy.random.randint(256, size=3)/255) for key in total_size_length_by_bitrate.keys()])

	barh_plot(sorted_artists_by_play_count_over_number_of_tracks, 'Average play count per song per artist', 'Play count')
	barh_plot(sorted_genres_by_play_count, 'Total play count by genre', 'Play count')
	barh_plot({artist: total_time / 60000 for artist, total_time in sorted(mbl.tagtrackers[5].data.items(), key=lambda item: item[1], reverse=True)}, 'Total time (min) by artist')
	barh_plot(sorted_artists_by_play_count, 'Play count per artist', 'Play count')
	barh_plot(sorted_artists_by_play_time, 'Play time per artist', 'Play time (h)')
	barh_plot(sorted_first_letter_song_name, 'Count of songs starting with letter')
	barh_plot(sorted_artists_by_play_size, 'Play size per artist', 'Play size (mb)')
	barh_plot(sorted_year_by_play_count, 'Play count by year', 'Play count')
	barh_plot(sorted_tracks_by_length, 'Amount of tracks per length interval of 30s')
	barh_plot(sorted_tracks_play_count_by_length, 'Play count per interval of length of song')
	barh_plot(sorted_artist_song_first_letter, 'Number of songs that start with the same letter as the artist name')
	barh_plot(sorted_album_by_play_count, 'Play count per album')
	barh_plot(sorted_album_by_play_time, 'Play time per album', x_label='Play time (h)')

	scatter_plot(numpy.array(scatter_name_time_length)[..., 0], numpy.array(scatter_name_time_length)[..., 1], 'Length of name vs length of song', x_label='Length of name', y_label='Length of song (s)')
	scatter_plot(x_data, y_data, 'Length of song vs size of song grouped by bitrate', subsets=True, color=color, label=groups, x_label='Length of song (s)', y_label='Size of song (mb)')

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


# Shows stats about the difference of play counts between the new library object and the old
def show_stats_over_time(date_new, new_mbl, date_old, old_mbl, update_rankings=False):
	rank_template = '{:0>2} {:0>4}-{:0>2}'  # regex: ([0-9]*) ([0-9]{4})-([0-9]{2})
	song_rankings = Config('mbls/stats/songs.mbr')
	album_rankings = Config('mbls/stats/albums.mbr')
	artist_rankings = Config('mbls/stats/artists.mbr')

	subbed_mbl = new_mbl - old_mbl
	sorted_subbed = sorted(subbed_mbl.tracks, key=lambda item: item.get('play_count'), reverse=True)

	tag_mbl = MBLibrary(tracks=subbed_mbl.tracks, tagtrackers=[
		TagTracker('artist', 'play_count', unique=False),
		TagTracker('artist', tag_data=lambda item: item.get('play_count') * item.get('total_time'), unique=False),
		TagTracker('album', 'play_count', unique=False),
		TagTracker('album', tag_data=lambda item: item.get('play_count') * item.get('total_time'), unique=False),

	])

	sorted_artist_play_count = sorted(tag_mbl.tagtrackers[0].data.items(), key=lambda item: item[1], reverse=True)
	sorted_albums_play_count = sorted(tag_mbl.tagtrackers[2].data.items(), key=lambda item: item[1], reverse=True)

	print('Over the last {} days you have added {} new songs and you listened to:'.format((date_new - date_old).days, len(new_mbl.tracks) - len(old_mbl.tracks)))

	# Print top 5 most listened to artists
	artists_base = '{:>2}. {:28.28}{:>5}{:>8.1f}h\n'
	artists_final = ''
	for i in range(0, 5):
		artists_final += artists_base.format(i+1, sorted_artist_play_count[i][0], sorted_artist_play_count[i][1], tag_mbl.tagtrackers[1].data[sorted_artist_play_count[i][0]]/3600000)
		if update_rankings:
			artist_rankings.add_value(sorted_artist_play_count[i][0], rank_template.format(i+1, date_new.year, date_new.month))

	print('Artists:')
	print(artists_final)

	# Print top 5 most listened to albums
	albums_base = '{:>2}. {:28.28}{:>5}{:>8.1f}h\n'
	albums_final = ''

	for i in range(0, 5):
		albums_final += albums_base.format(i + 1, sorted_albums_play_count[i][0], sorted_albums_play_count[i][1],
											tag_mbl.tagtrackers[3].data[sorted_albums_play_count[i][0]] / 3600000)
		if update_rankings:
			album_rankings.add_value(sorted_albums_play_count[i][0], rank_template.format(i+1, date_new.year, date_new.month))

	print('Albums:')
	print(albums_final)

	# Print top 5 most listened to songs
	songs_base = '{:>2}. {:28.28}{:>5}{:>8.1f}h\n'
	songs_final = ''
	for i in range(0, 10):
		songs_final += songs_base.format(i + 1, sorted_subbed[i].get('name'), sorted_subbed[i].get('play_count'), sorted_subbed[i].get('play_count') * sorted_subbed[i].get('total_time')/3600000)
		if update_rankings:
			song_rankings.add_value(sorted_subbed[i].get('name'), rank_template.format(i+1, date_new.year, date_new.month))

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

	files = glob.glob('mbls/*.mbl')
	diff = 0

	while not found:
		# Check the target date with + diff and - diff because either side of the date works
		# If we find a date that has an mbl file we return the MBLibrary and the date of that MBLibrary

		# Backward slash because glob returns the path with \\ not with /
		target_date = datetime.date(date.year, date.month, date.day) - datetime.timedelta(days=diff)
		target_file = 'mbls\\{:0>4}{:0>2}{:0>2}.mbl'.format(target_date.year, target_date.month, target_date.day)

		if target_file in files:
			return read_mbl(target_file), target_date

		target_date = datetime.date(date.year, date.month, date.day) + datetime.timedelta(days=diff)
		target_file = 'mbls\\{:0>4}{:0>2}{:0>2}.mbl'.format(target_date.year, target_date.month, target_date.day)

		if target_file in files:
			return read_mbl(target_file), target_date

		diff += 1


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('Use this program as follows: python main.py PATH_TO_FILE [-saveOnly]')
		sys.exit()

	# Load or create config
	config = Config('config.mbc')

	# Check if settings exist, otherwise create default
	if not config.get_setting('year'):
		config.set_setting('year', [1,1])
	if not config.get_setting('month'):
		config.set_setting('month', 1)

	file_path = sys.argv[1]

	if len(sys.argv) > 1 and '-saveOnly' in sys.argv:
		# User only wants to save the stats, not show any graphs and shit
		new_mbl = read_library_xml(file_path)
		save_library(new_mbl)

		today = datetime.date.today()

		# Check for first of the month or new year for stats
		if today.day == config.get_setting('month'):
			print('monthly')
			# Print monthly stats
			t_day = today.day
			t_month = 12 if today.month == 1 else today.month - 1
			t_year = today.year - 1 if t_month == 12 else today.year

			old_mbl, date_old = find_closest_mbl(datetime.date(t_year, t_month, t_day))
			show_stats_over_time(today, new_mbl, date_old, old_mbl, update_rankings=True)
		if today.day == config.get_setting('year')[0] and today.month == config.get_setting('year')[1]:
			print('yearly')
			# Print yearly stats
			old_mbl, date_old = find_closest_mbl(datetime.date(today.year - 1, today.month, today.day))
			show_stats_over_time(today, new_mbl, date_old, old_mbl)
	else:
		# User wants to see some interesting stuff
		show_stats(file_path)
