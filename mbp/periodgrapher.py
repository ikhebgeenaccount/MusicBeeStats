import datetime

import numpy as np
import matplotlib.pyplot as plt

import mbp.musicbeelibrary
from mbp import util
from mbp.musicbeelibrary import MBLibrary
from mbp.ranking import Ranking
from mbp.tagtracker import TagTracker


class PeriodGrapher:
	"""
	Class which displays informative plots of song listening behaviour over a set period of time.
	"""

	def __init__(self, start_date, end_date):
		"""
		:param start_date: datetime.datetime starting date
		:param end_date: datetime.datetime end date
		"""
		# Set dates
		self.start_date = start_date
		self.end_date = end_date

		# Find first mbl
		self.start_mbl, self.real_start_date = mbp.musicbeelibrary.find_closest_mbl(start_date - datetime.timedelta(days=1), diff_inc=-1)

		# Create arrays to store mbls
		self.total_days = (self.end_date - self.start_date).days + 1  # +1 to have an inclusive range for the end_date
		self.stats = [0.] * (self.total_days + 1)

		# TagTracker to calculate total amount of mins per artist
		total_tracker_artist_play_time = TagTracker('artist', tag_data=lambda item: item.get('play_count') * item.get('total_time') / 60000, unique=False)
		total_time = TagTracker(tag=lambda t: 'total_time', tag_data=lambda item: item.get('play_count') * item.get('total_time') / 60000, unique=False)

		# Has the mbl over the complete period
		self.period_mbl = MBLibrary(tracks=(
					mbp.musicbeelibrary.find_closest_mbl(self.end_date)[0] - self.start_mbl).tracks, tagtrackers=[total_tracker_artist_play_time, total_time])
		self.total_time_value = total_time.data['total_time']

		print(total_tracker_artist_play_time.data)

		self.artist_ranking = Ranking(total_tracker_artist_play_time)

		print(self.artist_ranking.get_string())

	def show_graphs_over_period(self, limit=0.2, window_size=4, allow_negative=False):
		"""
		Shows graphs about the given period from start_date to end_date.
		:param allow_negative:
		:param window_size:
		:param limit:
		:return:
		"""
		rest_key = 'Rest'

		# x coordinates for bar plot
		x = range(0, self.total_days)
		ys = []
		ys_keys = []

		# Determine how many different artists will be displayed

		for i in range(0, self.artist_ranking.get_length()):
			if self.artist_ranking.get_score(i, zero_indexed=True) / self.total_time_value >= limit:
				ys.append([0.] * self.total_days)
				ys_keys.append(self.artist_ranking.get_entry(i, zero_indexed=True))
			else:
				break

		ys.append([0.] * self.total_days)

		ys = np.array(ys)

		# Loop through all days in the period
		i = 0
		# prev_i is used to remember for what entry an mbl was found
		prev_i = 0
		while i < self.total_days + 1:
			target_date = self.real_start_date + datetime.timedelta(days=i)

			# TagTrackers to track stats for one day for each artist in ys_keys
			tts = []
			for artist in ys_keys:
				tts.append(TagTracker(tag=lambda t, artist=artist: artist if t.get('artist') == artist else None, tag_data=lambda item: item.get('play_count') * item.get('total_time') / 60000, unique=False))

			tts.append(TagTracker(tag=lambda t: rest_key if t.get('artist') not in ys_keys else None, tag_data=lambda item: item.get('play_count') * item.get('total_time') / 60000, unique=False))

			# We already know the first mbl
			if i == 0:
				MBLibrary(tracks=self.start_mbl.tracks, tagtrackers=tts)

				self.stats[i] = tts
				i += 1
				continue

			# Find closest mbl, add tagtrackers
			target_date_mbl, real_target_date = mbp.musicbeelibrary.find_closest_mbl(target_date, tagtrackers=tts)

			# Check if the dates match
			if target_date != real_target_date:
				# If not the same, skip i forward to the date for which we found this mbl
				i += (real_target_date - target_date).days

			# Enter the found mbls in the arrays
			self.stats[i] = tts

			# For every artist, add their value for this day to ys if they have a value
			for j in range(0, len(ys_keys)):
				if ys_keys[j] in tts[j].data:
					ys[j][i - 1] = (tts[j] - self.stats[prev_i][j]).data[ys_keys[j]]
					if not allow_negative and ys[j][i - 1] < 0:
						ys[j][i - 1] = 0

			# Now at rest, if applicable
			if rest_key in tts[-1].data:
				ys[-1][i - 1] = (tts[-1] - self.stats[prev_i][-1]).data[rest_key]
				if not allow_negative and ys[-1][i - 1] < 0:
					ys[-1][i - 1] = 0

			# Go next and remember this entry as prev_i
			prev_i = i
			i += 1

		fig, ax = plt.subplots()

		ax.bar(x, ys[-1], label=rest_key)

		# Keep track of the height of the current graph
		bottom = ys[-1]
		for i in range(0, len(ys) - 1):
			# Add new bars on top of current height
			ax.bar(x, ys[i], bottom=bottom, label=ys_keys[i])
			bottom += ys[i]

		# Now, bottom is the height of the graph at each point: the total time for each day
		sliding_window_avg = util.moving_average(bottom, window_size)

		ax.plot(x[window_size - 1:], sliding_window_avg, color='black', label=f'Sliding window average over {window_size} days')

		# Number of ticks
		ts = int(round(0.027 * self.total_days + 2.19))
		# magic function to have 12 ticks with 365 days and 3 ticks with 30 days

		ds_between = int(round(self.total_days / ts))

		days = range(0, self.total_days, ds_between)
		ticks = [(self.start_date + datetime.timedelta(days = i)).strftime('%b %d') for i in days]
		ax.set_xticks(days)
		ax.set_xticklabels(ticks)

		ax.set_ylabel('Play time (min)')

		ax.legend()

		plt.show()
