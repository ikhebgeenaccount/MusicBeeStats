import datetime

import numpy as np
import matplotlib.pyplot as plt

import main
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
		start_mbl, self.real_start_date = main.find_closest_mbl(start_date)

		# Create arrays to store mbls
		self.total_days = (self.end_date - self.start_date).days + 1  # +1 to have an inclusive range for the end_date
		self.mbls = np.empty(self.total_days, dtype=object)
		self.subbed_mbls = np.empty(self.total_days, dtype=object)

		# Dates are the dates that the mbls correspond to, meaning: filename of mbl - 1 day,
		# as they are saved the next day and named after the day of saving
		self.dates = np.empty(self.total_days, dtype=object)

		# Put start_mbl in the array
		self.mbls[0] = start_mbl
		self.subbed_mbls[0] = start_mbl - main.find_closest_mbl(self.start_date - datetime.timedelta(days=1), diff_inc=-1)[0]

		for i in range(self.total_days):
			self.dates[i] = self.real_start_date + datetime.timedelta(days=i - 1)

		# TagTracker to calculate total amount of mins per artist
		total_tracker_artist_play_time = TagTracker('artist', tag_data=lambda item: item.get('play_count') * item.get('total_time') / 60000, unique=False)
		total_time = TagTracker(tag=lambda t: 'total_time', tag_data=lambda item: item.get('play_count') * item.get('total_time') / 60000, unique=False)

		# Has the mbl over the complete period
		self.period_mbl = MBLibrary(tracks=(main.find_closest_mbl(self.end_date)[0] - self.mbls[0]).tracks, tagtrackers=[total_tracker_artist_play_time, total_time])
		self.total_time_value = total_time.data['total_time']

		self.artist_ranking = Ranking(total_tracker_artist_play_time)

	def show_graphs_over_period(self):
		"""
		Shows graphs about the given period from start_date to end_date.
		:param start_date: datetime.datetime starting date
		:param end_date: datetime.datetime end date
		:return:
		"""
		rest_key = 'Rest'

		# x coordinates for bar plot
		x = range(0, self.total_days)
		ys = []
		ys_keys = []

		# Determine how many different artists will be displayed
		# TODO: add argument to not hardcode the limit
		limit = 0.2

		for i in range(0, self.artist_ranking.get_length()):
			if self.artist_ranking.get_score(i, zero_indexed=True) / self.total_time_value >= limit:
				ys.append([0.] * self.total_days)
				ys_keys.append(self.artist_ranking.get_entry(i, zero_indexed=True))
			else:
				break

		ys.append([0.] * self.total_days)

		ys = np.array(ys)

		# Loop through all days in the period
		i = 1  # TODO: add day zero
		# prev_i is used to remember for what entry an mbl was found
		prev_i = 0
		while i < self.total_days:
			target_date = self.real_start_date + datetime.timedelta(days=i)

			# TagTrackers to track stats for one day for each artist in ys_keys
			tts = []
			for artist in ys_keys:
				tts.append(TagTracker(tag=lambda t, artist=artist: artist if t.get('artist') == artist else None, tag_data=lambda item: item.get('play_count') * item.get('total_time') / 60000, unique=False))

			tts.append(TagTracker(tag=lambda t: rest_key if t.get('artist') not in ys_keys else None, tag_data=lambda item: item.get('play_count') * item.get('total_time') / 60000, unique=False))

			# Find closest mbl, add tagtrackers
			target_date_mbl, real_target_date = main.find_closest_mbl(target_date)

			# Check if the dates match
			if target_date != real_target_date:
				# If not the same, skip i forward to the date for which we found this mbl
				i += (real_target_date - target_date).days

			# Enter the found mbls in the arrays
			self.mbls[i] = target_date_mbl
			self.subbed_mbls[i] = MBLibrary(tracks=(target_date_mbl - self.mbls[prev_i]).tracks, tagtrackers=tts)

			# For every artist, add their value for this day to ys if they have a value
			for j in range(0, len(ys_keys)):
				if ys_keys[j] in tts[j].data:
					ys[j][i] = tts[j].data[ys_keys[j]]

			# Now at rest, if applicable
			if rest_key in tts[-1].data:
				ys[-1][i] = tts[-1].data[rest_key]

			# if i == 211:
			# 	print(prev_i)
			# 	for t in self.subbed_mbls[i].tracks:
			# 		print(t.get('name'), t.get('play_count'))
			# 	for t in tts:
			# 		print(t.data)

			# Go next and remember this entry as prev_i
			prev_i = i
			i += 1

		fig, ax = plt.subplots()

		ax.bar(x, ys[-1], label=rest_key)

		min = ys[-1]
		for i in range(0, len(ys) - 1):
			ax.bar(x, ys[i], bottom=min, label=ys_keys[i])
			min += ys[i]

		ax.legend()
		plt.show()
