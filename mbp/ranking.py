FORMAT = '{:>3} {:28.28}'
FORMAT_DIFF = '{:>3}{:>5} {:28.28}'


class Ranking:
	"""
	A Ranking can display the data from a TagTracker in a ranked fashion.
	Other TagTrackers can be added to display multiple columns of data.

	Columns can be named with ColumnTitles.

	Change in the ranking order can be displayed using a different Ranking for diff_ranking.
	"""

	def __init__(self, tagtracker, data_format, diff_ranking=None, reverse=True, col_titles=None):
		"""
		:param tagtracker: The TagTracker from which this Ranking displays the data
		:param data_format: Format string for the data column, can also be an array of formats that will be applied in order. Value is applied to the first entry, then the resulting string to the second entry, etc.
		:param diff_ranking: The Ranking this will be compared with and the difference displayed, if ommited the difference column is not displayed
		:param reverse: Determines the order of sorting, default is from higher to lower
		:param col_titles: Accepts an list with two ColumnTitles, first member for the identifier (tag), second for the data (tag_data) in the passed TagTracker
		"""
		self.tagtracker = tagtracker
		self.data_format = data_format
		self.col_titles = col_titles

		self.sorted_keys = [i[0] for i in sorted(self.tagtracker.data.items(), key=lambda item: item[1], reverse=reverse)]

		self.diff_ranking = diff_ranking

		self.extra_tagtrackers = []
		self.extra_data_formats = []
		self.extra_cols = []

	def get_ranking(self, key):
		return self.sorted_keys.index(key)

	def get_entry(self, placement, zero_indexed=False):
		return self.sorted_keys[placement - (0 if zero_indexed else 1)]

	def get_score(self, placement, zero_indexed=False):
		return self.tagtracker.data[self.get_entry(placement, zero_indexed)]

	def add_tagtracker(self, tagtracker, data_format, col_title=None):
		self.extra_tagtrackers.append(tagtracker)
		self.extra_data_formats.append(data_format)
		self.extra_cols.append(col_title)

	def get_string(self, count=10):
		"""
		:param count: the amount of lines to print of the ranking (e.g. count=10 prints the top 10)
		:return: string with top count, with all data from extra tagtrackers and column titles
		"""
		if count > len(self.sorted_keys):
			# warn('Count is higher than number of entries, printing all.')
			count = len(self.sorted_keys)

		# First line should be generated with column titles if we have those
		if self.col_titles:
			# First two columns
			if self.diff_ranking:
				res = FORMAT_DIFF.format('', '', self.col_titles[0].get_title()) + self.col_titles[1].get_title()
			else:
				res = FORMAT.format('', self.col_titles[0].get_title()) + self.col_titles[1].get_title()

			# Check for extra column titles
			for i in range(0, len(self.extra_cols)):
				if self.extra_cols[i]:
					res += self.extra_cols[i].get_title()
			res += '\n'
		else:
			res = ''

		# Append the top <count>
		for i in range(0, count):
			# Get this entries key
			curr_entry = self.sorted_keys[i]

			# Generate string from extra_tagtrackers
			extra_str = ''
			for j in range(0, len(self.extra_tagtrackers)):
				# Add formatted data from the extra tagtrackers for curr_entry
				if type(self.extra_data_formats[j]) is list:
					f_s = ''
					for k in range(0, len(self.extra_data_formats[j])):
						if k == 0:
							f_s = self.extra_data_formats[j][k].format(self.extra_tagtrackers[j].data[curr_entry])
						else:
							f_s = self.extra_data_formats[j][k].format(f_s)

					extra_str += f_s
				else:
					extra_str += self.extra_data_formats[j].format(self.extra_tagtrackers[j].data[curr_entry])

			# Generate entry and append extra_str
			if self.diff_ranking:
				try:
					diff_value = self.diff_ranking.get_ranking(curr_entry) - self.sorted_keys.index(curr_entry)

					diff_string = '({:+d})'.format(diff_value)
					res += FORMAT_DIFF.format(str(i + 1) + '.', diff_string, curr_entry) + self.data_format.format(self.tagtracker.data[curr_entry]) + extra_str + '\n'
				except ValueError:
					res += FORMAT_DIFF.format(str(i + 1) + '.', '(+' + str(len(self.sorted_keys) - i) + ')', curr_entry) + self.data_format.format(self.tagtracker.data[curr_entry]) + extra_str + '\n'
			else:
				res += FORMAT.format(str(i + 1) + '.', curr_entry) + self.data_format.format(self.tagtracker.data[curr_entry]) + extra_str + '\n'

		return res


class ColumnTitle:

	def __init__(self, title, title_format='{}'):
		self.title = title
		self.title_format = title_format

	def get_title(self):
		return self.title_format.format(self.title)