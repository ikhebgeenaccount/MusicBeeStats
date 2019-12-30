import os


def create_path(path):
	"""Creates path if it does not exist yet. Returns path."""
	# If the path does not exist create it dir by dir
	if not os.path.exists(path):
		if '/' in path:
			dirs = path.split('/')
		else:
			dirs = path.split('\\')
		# The last part of dirs is the filename itself which will be created with the open call later
		for i in range(0, len(dirs) - 1):
			if not os.path.exists(os.path.join(*dirs[0:i + 1])):
				os.mkdir(os.path.join(*dirs[0:i + 1]))
	return path