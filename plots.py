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


def scatter_plot(x, y, title, subsets=False, x_label=None, y_label=None, color=None, label=None):
	plt.rcdefaults()
	fig, ax = plt.subplots()

	# Add data
	if not subsets:
		ax.scatter(x, y, s=1)
	else:
		for i in range(0, len(x)):
			ax.scatter(x[i], y[i], c=[color[i]], label=label[i], s=5)
		ax.legend(loc=4, ncol=3)

	# Set title
	ax.set_title(title)

	# Set axis labels
	if x_label:
		ax.set_xlabel(x_label)
	if y_label:
		ax.set_ylabel(y_label)