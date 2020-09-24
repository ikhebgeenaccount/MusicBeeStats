import numpy


class Recommender:

	def __init__(self, ranking, lastfm_api, based_on=5, amount=5, weight=lambda p: 1 - 0.01 * (p - 1)):
		self.ranking = ranking
		self.based_on = based_on
		self.amount = amount
		self.lastfm_api = lastfm_api
		self.weight = weight  # TODO: scale weight with the score in assiciated Ranking?
		self.max_score = sum([self.weight(p) for p in range(1, self.based_on)])

	def get_recommendations(self, based_on=None, amount=None):
		if based_on:
			self.based_on = based_on
			self.max_score = sum([self.weight(p) for p in range(1, self.based_on)])
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
					recommendations[s] += self.weight(n + 1)
				else:
					recommendations[s] = self.weight(n + 1)

		recs_sorted = [[i[0], i[1], i[1] / self.max_score] for i in sorted(recommendations.items(), key=lambda item: item[1], reverse=True)]

		return recs_sorted[0:self.amount]