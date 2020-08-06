FORMAT = '{:>3} {:28.28}'
FORMAT_DIFF = '{:>3}{:>5} {:28.28}'

# TODO: titles for columns
# TODO: diff for place in ranking
# TODO: diff for values like play count


class Ranking:
	"""

	"""

	def __init__(self, tagtracker, data_format, diff_ranking=None, reverse=True, col_titles=None):
		self.tagtracker = tagtracker
		self.data_format = data_format
		self.col_titles = col_titles

		self.sorted_keys = [i[0] for i in sorted(self.tagtracker.data.items(), key=lambda item: item[1], reverse=reverse)]

		self.diff_ranking = diff_ranking

		self.extra_tagtrackers = []
		self.extra_data_formats = []
		self.extra_cols = []

	def get_ranking(self, key):
		try:
			return self.sorted_keys.index(key)
		except ValueError:
			print('ve')
			return len(self.sorted_keys)

	def add_tagtracker(self, tagtracker, data_format, col_title=None):
		self.extra_tagtrackers.append(tagtracker)
		self.extra_data_formats.append(data_format)
		self.extra_cols.append(col_title)

	def get_string(self, count=10):
		"""
		:param count: the amount of lines to print of the ranking (e.g. count=10 prints the top 10)
		:return: string with top 10, with all data from extra tagtrackers and column titles
		"""
		# Print the top <count>
		if self.col_titles:
			# First two columns
			if self.diff_ranking:
				res = FORMAT_DIFF.format('', '', self.col_titles[0].get_title()) + self.col_titles[1].get_title()
			else:
				res = FORMAT.format('', self.col_titles[0]) + self.data_format.format(self.col_titles[1])

			# Check for extra column titles
			for i in range(0, len(self.extra_cols)):
				if self.extra_cols[i]:
					res += self.extra_cols[i].get_title()
			res += '\n'
		else:
			res = ''

		for i in range(0, count):
			# Get this entries key
			curr_entry = self.sorted_keys[i]

			# Generate string from extra_tagtrackers
			extra_str = ''
			for j in range(0, len(self.extra_tagtrackers)):
				# Add formatted data from the extra tagtrackers for curr_entry
				extra_str += self.extra_data_formats[j].format(self.extra_tagtrackers[j].data[curr_entry])

			if self.diff_ranking:
				try:
					diff_value = self.diff_ranking.get_ranking(curr_entry) - self.sorted_keys.index(curr_entry)
					if diff_value > 0:
						diff_string = '(+' + str(diff_value) + ')'
					elif diff_value < 0:
						diff_string = '(' + str(diff_value) + ')'
					else:
						diff_string = '(0)'
					res += FORMAT_DIFF.format(str(i + 1) + '.', diff_string, curr_entry) + self.data_format.format(self.tagtracker.data[curr_entry]) + extra_str + '\n'
				except ValueError:
					res += FORMAT_DIFF.format(str(i + 1) + '.', '(+' + self.diff_ranking.get_ranking(curr_entry), curr_entry) + ')' + self.data_format.format(self.tagtracker.data[curr_entry]) + extra_str + '\n'
			else:
				res += FORMAT.format(str(i + 1) + '.', curr_entry) + self.data_format.format(self.tagtracker.data[curr_entry]) + extra_str + '\n'

		return res


class ColumnTitle:

	def __init__(self, title, title_format='{}'):
		self.title = title
		self.title_format = title_format

	def get_title(self):
		return self.title_format.format(self.title)