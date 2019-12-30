import re
import util


def convert_values(values):
	"""Attempts to convert list of values to integers, if that does not succeed it tries floats, if that doesn not
	succeed it returns the original list. """
	try:
		return [int(x) for x in values]
	except ValueError:
		try:
			return [float(x) for x in values]
		except ValueError:
			return values


class Config:
	"""Config file handling."""

	def __init__(self, file_path=None, settings=None):
		if settings:
			self.settings = settings
		else:
			self.settings = {}

		if file_path:
			self.file_path = file_path
			try:
				self.read_config(file_path)
			except IOError:
				pass

	def get_setting(self, setting):
		"""Returns the value of setting."""
		if setting in self.settings:
			return self.settings[setting]
		return None

	def set_setting(self, setting, value):
		"""Changes the value of setting to value and saves the settings to disk."""
		if type(setting) is str and '=' in setting:
			raise ValueError(f'= in {setting} but not allowed in setting name.')
		if type(value) is str and ',' in value:
			raise ValueError(f', in {value} but not allowed in setting value.')
		self.settings[setting] = value
		self.save_settings()

	def add_value(self, setting, value):
		"""Adds value to the setting, appending to anything already there."""
		if setting not in self.settings.keys():
			self.set_setting(setting, value)
		else:
			if type(self.get_setting(setting)) is list:
				self.get_setting(setting).append(value)
				self.save_settings()
			else:
				self.set_setting(setting, [self.get_setting(setting), value])

	def save_settings(self, file_path=None):
		"""Saves the settings to disk. If no file_path is specified anywhere raises a ValueError."""
		# Check if we have any file path
		if not file_path and not self.file_path:
			raise ValueError('No file path specified')

		# Passed file path to this function takes precedence over stored file path in instance
		path = file_path if file_path else self.file_path

		util.create_path(path)

		# Save the settings to path
		with open(path, 'w', encoding='utf-8') as out:
			template = '{}={}\n'
			for key in self.settings.keys():
				value = self.settings[key]
				if type(value) is list:
					r = ''
					for v in value:
						r += v + ','
					r = r[0:-1]  # Get rid of the trailing comma
					out.write(template.format(key, r))
				else:
					out.write(template.format(key, value))

	def read_config(self, file_path):
		"""Reads the file at file_path into a Config, and returns that Config."""
		with open(file_path, 'r', encoding='utf-8') as config_file:
			pattern = re.compile('^(.*)=[(.*),]*(.*)$')
			self.settings = {}
			for line in config_file:
				m = pattern.match(line)
				name = m.group(1)  # name of setting
				values = m.group(2).split(',')  # value(s) of setting
				if len(values) > 1:
					# List of values
					self.settings[name] = convert_values(values)
				else:
					# Only one value
					self.settings[name] = convert_values(values)[0]
