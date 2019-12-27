import numpy
from matplotlib import pyplot as plt


def barh_plot(d, title, x_label=None, y_label=None):
	"""Creates a horizontal bar plot of the data in dictionary d with keys as labels and values as values."""
	plt.rcdefaults()
	fig, ax = plt.subplots()

	# Add data
	ax.barh(list(d.keys()), list(d.values()))

	# Set title
	ax.set_title(title)

	# Set axis labels
	if x_label:
		ax.set_xlabel(x_label)
	if y_label:
		ax.set_ylabel(y_label)

	# Set data labels
	ax.set_yticklabels(d.keys())
	ax.invert_yaxis()  # idk why tbh


def scatter_plot(nparr, title, x_label=None, y_label=None):
	"""Creates a scatter plot of the date in dictionary with keys as x values and values as y values."""
	plt.rcdefaults()
	fig, ax = plt.subplots()

	# Add data
	ax.scatter(nparr[..., 0], nparr[..., 1], s=1)

	# Set title
	ax.set_title(title)

	# Set axis labels
	if x_label:
		ax.set_xlabel(x_label)
	if y_label:
		ax.set_ylabel(y_label)
