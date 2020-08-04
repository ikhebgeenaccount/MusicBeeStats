FORMAT = '{:>2}. {:28.28}'
FORMAT_DIFF = '{:>2}.({:>3}) {:28.28}'
FORMAT_EXTRA = '{:>5}'

# TODO: titles for columns
# TODO: diff for place in ranking
# TODO: diff for values like play count


class Ranking:
	"""

	"""

	def __init__(self, tagtracker, data_format, diff_standing=None, reverse=True):
		self.tagtracker = tagtracker
		self.data_format = data_format

		self.sorted_data = sorted(self.tagtracker.data.items(), key=lambda item: item[1], reverse=reverse)

		self.diff_standing = diff_standing

		self.extra_tagtrackers = []
		self.extra_data_formats = []

	def get_ranking(self, key):
		# TODO for diff in ranking
		pass

	def add_tagtracker(self, tagtracker, data_format):
		self.extra_tagtrackers.append(tagtracker)
		self.extra_data_formats.append(data_format)

	def get_string(self, count=10):
		# Print the top <count>
		res = ''
		for i in range(0, count):
			# Get this entries key
			curr_entry = self.sorted_data[i][0]

			# Generate string from extra_tagtrackers
			extra_str = ''
			for j in range(0, len(self.extra_tagtrackers)):
				# Add formatted data from the extra tagtrackers for curr_entry
				extra_str += FORMAT_EXTRA.format(self.extra_data_formats[j].format(self.extra_tagtrackers[j].data[curr_entry]))

			res += FORMAT.format(i + 1, curr_entry) + self.data_format.format(self.tagtracker.data[curr_entry]) + extra_str + '\n'

		return res
