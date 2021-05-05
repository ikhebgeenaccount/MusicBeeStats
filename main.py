import datetime
import glob
import json
import os
import sys

import dateutil
import matplotlib.pyplot as plt
import numpy

from lastfm.lastfmapi import LastFMAPI
from mbp.config import Config
from mbp.musicbeelibrary import MBLibrary
from mbp.periodgrapher import PeriodGrapher
from mbp.plots import barh_plot, scatter_plot
from mbp.ranking import Ranking, ColumnTitle
from mbp.recommender import Recommender
from mbp.tagtracker import TagTracker
from mbp.track import Track


# TODO: fix MBLirary subtraction: subtracting one from itself results in ValueError (MBLibrary tracks list is empty which results in (if tracks:) being false)


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
		TagTracker(tag=lambda t: int(t.get('total_time') / 1000 - (t.get('total_time') / 1000) % 30)),
		# Sums the play count for each interval of 30s of length of songs
		TagTracker(tag=lambda t: int(t.get('total_time') / 1000 - (t.get('total_time') / 1000) % 30),
				   tag_data='play_count', unique=False),
		# Counts the number of songs of artists that start with the same letter as the artists' names
		TagTracker(tag='artist', tag_data=lambda t: t.get('artist')[0] == t.get('name')[0], unique=False),
		# Tracks the length of songs for each name length
		TagTracker(tag=lambda t: len(t.get('name')), tag_data=lambda t: t.get('total_time')),
		# Tracks the total time and size per bitrate
		TagTracker(tag='bitrate', tag_data=lambda t: [t.get('total_time'), t.get('size')]),

		# Counts the play count per album
		TagTracker(tag='album', tag_data='play_count', unique=False),
		# Sums the total time listened to per album
		TagTracker(tag='album', tag_data=lambda t: t.get('play_count') * t.get('total_time'), unique=False),

		TagTracker(tag=lambda t: int(t.get('play_count') - (t.get('play_count') % 100))),
	])

	print(('{:20}{}\n' * 4 + '{:20}{:.1f}{}\n' * 3 + '{} {}, {} times for a total of {:.1f} hours')
		  .format('Tracks found:', len(mbl.tracks),
				  'Artists found:', len(mbl.tagtrackers[2].data),
				  'File size:', str(round(sum(mbl.tracks).get('size') / (1024 ** 3), 1)) + 'GB',
				  'Total play count:', sum(mbl.tracks).get('play_count'),
				  'Average play count:', sum(mbl.tracks).get('play_count') / len(mbl.tracks), '',
				  'Total time:', sum(mbl.tracks).get('total_time') / 3600000, 'h',
				  'Total time played:',
				  sum([track.get('play_count') * track.get('total_time') for track in mbl.tracks]) / 3600000, 'h',
				  'Most played:', max(mbl.tracks).get('name'), max(mbl.tracks).get('play_count'),
				  max(mbl.tracks).get('total_time') * max(mbl.tracks).get('play_count') / 3600000))

	# print(mbl.tagtrackers[-1].data)

	sorted_artists_by_play_count = {artist: play_count for artist, play_count in
									sorted(mbl.tagtrackers[0].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_genres_by_play_count = {genre: play_count for genre, play_count in
								   sorted(mbl.tagtrackers[1].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_artists_by_play_count_over_number_of_tracks = {artist: play_count / mbl.tagtrackers[2].data[artist] for
														  artist, play_count in sorted(
			filter(lambda elem: mbl.tagtrackers[2].data[elem[0]] > 10, mbl.tagtrackers[0].data.items()),
			key=lambda item: item[1] / mbl.tagtrackers[2].data[item[0]], reverse=True)}
	sorted_artists_by_play_time = {artist: play_time / 3600000 for artist, play_time in
								   sorted(mbl.tagtrackers[6].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_first_letter_song_name = {letter: count for letter, count in
									 sorted(mbl.tagtrackers[7].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_artists_by_play_size = {artist: size / (1024 ** 2) for artist, size in
								   sorted(mbl.tagtrackers[8].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_year_by_play_count = {str(year): play_count for year, play_count in
								 sorted(mbl.tagtrackers[9].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_tracks_by_length = {'{} - {}'.format(base, base + 30): count for base, count in
							   sorted(mbl.tagtrackers[10].data.items(), key=lambda item: item[0])}
	sorted_tracks_play_count_by_length = {'{} - {}'.format(base, base + 30): count for base, count in
										  sorted(mbl.tagtrackers[11].data.items(), key=lambda item: item[0])}
	sorted_artist_song_first_letter = {artist: count for artist, count in
									   sorted(mbl.tagtrackers[12].data.items(), key=lambda item: item[1], reverse=True)}
	sorted_album_by_play_count = {album: play_count for album, play_count in
								  sorted(mbl.tagtrackers[15].data.items(), key=lambda item: item[1], reverse=True) if
								  play_count > 500}
	sorted_album_by_play_time = {album: round(play_time / 3600000, 0) for album, play_time in
								 sorted(mbl.tagtrackers[16].data.items(), key=lambda item: item[1], reverse=True) if
								 play_time > 24 * 3600000}
	sorted_tracks_by_play_count_interval = {'{} - {}'.format(base, base + 100): (mbl.tagtrackers[17].data[base] if base in mbl.tagtrackers[17].data.keys() else 0) for base in range(min(mbl.tagtrackers[17].data.keys()), max(mbl.tagtrackers[17].data.keys()) + 100, 100)}

	scatter_name_time_length = []
	for key in mbl.tagtrackers[13].data.keys():
		for val in mbl.tagtrackers[13].data[key]:
			scatter_name_time_length.append([key, val / 1000])

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
					y_data[c].append(round(value / (1024 ** 2), 2))
				else:
					x_data[c].append(round(value / 1000, 2))
				counter += 1
		c += 1

	x_data = numpy.asarray(x_data)
	y_data = numpy.asarray(y_data)

	color = numpy.asarray(
		[tuple(numpy.random.randint(256, size=3) / 255) for key in total_size_length_by_bitrate.keys()])

	barh_plot(sorted_artists_by_play_count_over_number_of_tracks, 'Average play count per song per artist',
			  'Play count')
	barh_plot(sorted_genres_by_play_count, 'Total play count by genre', 'Play count')
	barh_plot({artist: total_time / 60000 for artist, total_time in
			   sorted(mbl.tagtrackers[5].data.items(), key=lambda item: item[1], reverse=True)},
			  'Total time (min) by artist')
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
	barh_plot(sorted_tracks_by_play_count_interval, 'Number of tracks per play count interval of 100', y_scale='log')
	barh_plot(sorted_tracks_by_play_count_interval, 'Number of tracks per play count interval of 100')

	scatter_plot(numpy.array(scatter_name_time_length)[..., 0], numpy.array(scatter_name_time_length)[..., 1],
				 'Length of name vs length of song', x_label='Length of name', y_label='Length of song (s)')
	scatter_plot(x_data, y_data, 'Length of song vs size of song grouped by bitrate', subsets=True, color=color,
				 label=groups, x_label='Length of song (s)', y_label='Size of song (mb)')

	# Show all created plots
	plt.show()


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


# Shows stats about the difference of play counts between the new library object and the old
def show_stats_over_time(date=datetime.date.today(), month_diff=1):
	# Find relevant MBLibraries
	new_mbl, new_mbl_date = find_closest_mbl(date)
	old_mbl, old_mbl_date = find_closest_mbl(date - dateutil.relativedelta.relativedelta(months=month_diff))
	oldest_mbl, oldest_mbl_date = find_closest_mbl(date - dateutil.relativedelta.relativedelta(months=month_diff * 2))

	# Subtract the old stats from the new stats to get the stats over time
	subbed_mbl = new_mbl - old_mbl

	# Get the stats from the last overview
	old_subbed_mbl = old_mbl - oldest_mbl

	# Track stats
	new_tracker_artist_play_count = TagTracker('artist', 'play_count', unique=False)
	new_tracker_artist_song_count = TagTracker('artist')
	new_tracker_artist_play_time = TagTracker('artist', tag_data=lambda item: item.get('play_count') * item.get('total_time') / 3600000, unique=False)
	new_tracker_album_play_count = TagTracker('album', 'play_count', unique=False)
	new_tracker_album_play_time = TagTracker('album', tag_data=lambda item: item.get('play_count') * item.get('total_time') / 3600000, unique=False)
	new_tracker_song_play_count = TagTracker('name', 'play_count', unique=False)
	new_tracker_song_play_count_track = TagTracker(lambda t: t, 'play_count', unique=False)
	new_tracker_song_play_time = TagTracker('name', tag_data=lambda item: item.get('play_count') * item.get('total_time') / 3600000, unique=False)
	new_tracker_artist_song_name = TagTracker('artist', tag_data=lambda item: None if item.get('play_count') == 0 else 1, unique=False)
	new_tag_mbl = MBLibrary(tracks=subbed_mbl.tracks, tagtrackers=[
		new_tracker_artist_play_count,
		new_tracker_artist_song_count,
		new_tracker_artist_play_time,
		new_tracker_album_play_count,
		new_tracker_album_play_time,
		new_tracker_song_play_count,
		new_tracker_song_play_count_track,
		new_tracker_song_play_time,
		new_tracker_artist_song_name
	])

	old_tracker_artist_play_count = TagTracker('artist', 'play_count', unique=False)
	old_tracker_artist_song_count = TagTracker('artist')
	old_tracker_artist_play_time = TagTracker('artist', tag_data=lambda item: item.get('play_count') * item.get('total_time') / 3600000, unique=False)
	old_tracker_album_play_count = TagTracker('album', 'play_count', unique=False)
	old_tracker_album_play_time = TagTracker('album', tag_data=lambda item: item.get('play_count') * item.get('total_time') / 3600000, unique=False)
	old_tracker_song_play_count = TagTracker('name', 'play_count', unique=False)
	old_tag_mbl = MBLibrary(tracks=old_subbed_mbl.tracks, tagtrackers=[
		old_tracker_artist_play_count,
		old_tracker_artist_song_count,
		old_tracker_artist_play_time,
		old_tracker_album_play_count,
		old_tracker_album_play_time,
		old_tracker_song_play_count
	])

	# Create Artist ranking
	artist_ranking = Ranking(new_tracker_artist_play_count, '{:>5}', diff_ranking=Ranking(old_tracker_artist_play_count, '{:>5}'), col_titles=[ColumnTitle('Artist'), ColumnTitle('Plays', '{:>5}')])
	artist_ranking.add_tagtracker(new_tracker_artist_play_count - old_tracker_artist_play_count, ['({:+d})', '{:>7}'], col_title=ColumnTitle('', '{:6}'))
	artist_ranking.add_tagtracker(new_tracker_artist_play_time, '{:>8.1f}h', col_title=ColumnTitle('Time', '{:>10}'))
	artist_ranking.add_tagtracker(new_tracker_artist_song_count, '{:>7}', col_title=ColumnTitle('Songs', '{:>7}'))

	# Create Album ranking
	album_ranking = Ranking(new_tracker_album_play_count, '{:>5}', diff_ranking=Ranking(old_tracker_album_play_count, '{:>5}'), col_titles=[ColumnTitle('Album'), ColumnTitle('Plays')])
	album_ranking.add_tagtracker(new_tracker_album_play_count - old_tracker_album_play_count, ['({:+d})', '{:>7}'], col_title=ColumnTitle('', '{:6}'))
	album_ranking.add_tagtracker(new_tracker_album_play_time, '{:>8.1f}h', col_title=ColumnTitle('Time', '{:>10}'))

	# Create Song ranking
	song_ranking = Ranking(new_tracker_song_play_count, '{:>5}', diff_ranking=Ranking(old_tracker_song_play_count, '{:>5}'), col_titles=[ColumnTitle('Song'), ColumnTitle('Plays')])
	song_ranking.add_tagtracker(new_tracker_song_play_count - old_tracker_song_play_count, ['({:+d})', '{:>7}'], col_title=ColumnTitle('', '{:6}'))
	song_ranking.add_tagtracker(new_tracker_song_play_time, '{:>8.1f}h', col_title=ColumnTitle('Time', '{:>10}'))

	# Create recommendations
	api_settings = Config('lastfmapi.mbc')
	api = LastFMAPI(key=api_settings.get_setting('api_key')[0])
	ranking_t = Ranking(new_tracker_song_play_count_track, '{:>5}')
	recommender = Recommender(ranking_t, api, based_on=15, amount=10)

	# Print all the stuff
	print('Over the last {} days you have added {} new songs and you listened to:'.format((new_mbl_date - old_mbl_date).days, len(new_mbl.tracks) - len(old_mbl.tracks)))

	# Print top 5 most listened to artists
	new_artist_count = sum([1 for p_c in new_tracker_artist_play_count.data.values() if p_c > 0])
	old_artist_count = sum([1 for p_c in old_tracker_artist_play_count.data.values() if p_c > 0])
	print('{} ({:+d}) artists:'.format(new_artist_count, new_artist_count - old_artist_count))
	print(artist_ranking.get_string(count=10))

	# Print top 5 most listened to albums
	new_album_count = sum([1 for p_c in new_tracker_album_play_count.data.values() if p_c > 0])
	old_album_count = sum([1 for p_c in old_tracker_album_play_count.data.values() if p_c > 0])
	print('{} ({:+d}) albums:'.format(new_album_count, new_album_count - old_album_count))
	print(album_ranking.get_string(count=10))

	# Print top 5 most listened to songs
	new_song_count = sum([1 for t in new_tag_mbl.tracks if t.get('play_count') > 0])
	old_song_count = sum([1 for t in old_tag_mbl.tracks if t.get('play_count') > 0])
	print('{} ({:+d}) songs:'.format(new_song_count, new_song_count - old_song_count))
	print(song_ranking.get_string(count=10))

	# Print top 10 risers
	print('Biggest increases:')
	print(Ranking(new_tracker_song_play_count - old_tracker_song_play_count, '{:+5d}', col_titles=[ColumnTitle('Song'), ColumnTitle('Increase')]).get_string())

	# Print top 10 fallers
	print('Biggest decreases:')
	print(Ranking(new_tracker_song_play_count - old_tracker_song_play_count, '{:+5d}', col_titles=[ColumnTitle('Song'), ColumnTitle('Decrease')], reverse=False).get_string())

	# TODO: populate fake tagtrackers and use ranking
	# Print recommendations
	print('Based on the songs you have listened to most this month, you might also like:')
	format_string = '{:<16.16} {:<24.24} {:<4}'
	print(format_string.format('Artist', 'Song', 'Match'))
	for r in recommender.get_recommendations():
		print(format_string.format(r[0].get('artist'), r[0].get('name'), f'{r[2] * 100:.1f}%'))

	print()

	# Print total stats
	print('All combined this makes for:\n'
		  ' {} total play count\n'
		  ' {:.1f}h total hours listened'
		  .format(str(sum(new_tag_mbl.tracks).get('play_count')),
				  sum([track.get('play_count') * track.get('total_time') for track in new_tag_mbl.tracks]) / 3600000))

	pg = PeriodGrapher(date, date - dateutil.relativedelta.relativedelta(months=month_diff))

	pg.show_graphs_over_period(limit=0.05, window_size=7)

	print('\nPress enter to close this overview')
	input()


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


if __name__ == '__main__':

	if len(sys.argv) < 2:
		print('Use this program as follows: python main.py PATH_TO_FILE [-saveOnly]')
		sys.exit()

	# Load or create config
	config = Config('config.mbc')

	# Check if settings exist, otherwise create default
	if not config.get_setting('year'):
		config.set_setting('year', [1, 1])
	if not config.get_setting('month'):
		config.set_setting('month', 1)

	file_path = sys.argv[1]

	if len(sys.argv) > 1 and '-saveOnly' in sys.argv:
		# User only wants to save the stats, not show any graphs and shit
		new_mbl = read_library_xml(file_path)

		save_library(new_mbl)

		today = datetime.date.today()

		# Check for first of the month or new year for stats
		if today.day == config.get_setting('month')[0]:
			show_stats_over_time()
		if today.day == config.get_setting('year')[0] and today.month == config.get_setting('year')[1]:
			# Print yearly stats
			show_stats_over_time(month_diff=12)
	else:
		# User wants to see some interesting stuff
		show_stats(file_path)
