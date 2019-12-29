import os
import re


def read_config(file_path):
	"""Reads the file at file_path into a Config, and returns that Config."""
	pattern = re.compile('^(.*)=[(.*),]*(.*)$')
	settings = {}
	with open(file_path, 'r') as config_file:
		for line in config_file:
			m = pattern.match(line)
			name = m.group(1)  # name of setting
			values = m.group(2).split(',')  # value(s) of setting
			if len(values) > 1:
				# List of values
				settings[name] = values
			else:
				# Only one value
				settings[name] = values[0]

	return Config(file_path=file_path, settings=settings)


class Config:
	"""Config file handling.

	Do NOT enter commas into the values for settings. It will break."""

	def __init__(self, file_path=None, settings=None):
		if file_path:
			self.file_path = file_path

		if settings:
			self.settings = settings
		else:
			self.settings = {}

	def get_setting(self, setting):
		"""Returns the value of setting."""
		if setting in self.settings:
			return self.settings[setting]
		return None

	def set_setting(self, setting, value):
		"""Changes the value of setting to value and saves the settings to disk."""
		self.settings[setting] = value
		self.save_settings()

	def save_settings(self, file_path=None):
		"""Saves the settings to disk. If no file_path is specified anywhere raises a ValueError."""
		# Check if we have any file path
		if not file_path and not self.file_path:
			raise ValueError('No file path specified')

		# Passed file path to this function takes precedence over stored file path in instance
		path = file_path if file_path else self.file_path

		# If the path does not exist create it dir by dir
		if not os.path.exists(path):
			if '/' in path:
				dirs = path.split('/')
			else:
				dirs = path.split('\\')
			# The last part of dirs is the filename itself which will be created with the open call later
			for i in range(0, len(dirs) - 1):
				if not os.path.exists(os.path.join(*dirs[0:i+1])):
					os.mkdir(os.path.join(*dirs[0:i+1]))

		# Save the settings to path
		with open(path, 'w') as out:
			template = '{}={}\n'
			for key in self.settings.keys():
				value = self.settings[key]
				if type(value) is list:
					out.write(template.format(key, str(value)[1:-1].replace(', ', ',')))
				else:
					out.write(template.format(key, value))
