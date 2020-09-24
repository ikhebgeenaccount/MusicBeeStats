

class Recommender:
	"""
	Recommender creates recommendations based on a Ranking.
	This Ranking has to be about Tracks, otherwise it will not work.
	"""

	def __init__(self, ranking, lastfm_api, based_on=5, amount=5):
		self.ranking = ranking
		self.based_on = min(based_on, len(self.ranking.sorted_keys))
		self.amount = amount
		self.lastfm_api = lastfm_api
		self.max_score = sum([self.ranking.get_score(i, zero_indexed=True) for i in range(0, self.based_on)])

	def get_recommendations(self, based_on=None, amount=None):
		if based_on:
			self.based_on = min(based_on, len(self.ranking.sorted_keys))
			self.max_score = sum([self.ranking.get_score(i, zero_indexed=True) for i in range(0, self.based_on)])
			print(self.max_score)
		if amount:
			self.amount = amount

		# Get top entries
		entries = []
		for i in range(1, self.based_on + 1):
			entries.append(self.ranking.get_entry(i))

		recommendations = {}

		for n in range(0, len(entries)):
			e = entries[n]
			similars = self.lastfm_api.get_similar_tracks_sanitized(e.get('artist'), e.get('name'))
			for s in similars:
				if s in recommendations:
					recommendations[s] += self.ranking.get_score(n, zero_indexed=True)
				else:
					recommendations[s] = self.ranking.get_score(n, zero_indexed=True)

		recs_sorted = [[i[0], i[1], i[1] / self.max_score] for i in sorted(recommendations.items(), key=lambda item: item[1], reverse=True)]

		return recs_sorted[0:self.amount]