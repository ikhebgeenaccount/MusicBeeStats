import json

import requests

from mbp.track import Track

API_ROOT = 'http://ws.audioscrobbler.com/2.0/?api_key={}&method={}&format=json{}'


class LastFMAPI:

	def __init__(self, key, secret='', registered_to='', application_name=''):
		"""
		:param key:
		:param secret:
		:param registered_to:
		:param application_name:
		"""
		self.key = key
		self.secret = secret
		self.registered_to = registered_to
		self.application_name = application_name

	def request(self, method, args):
		"""
		Returns the REST endpoint json formatted data from the LastFM API
		:param method: the method to use
		:param args: arguments to add to the url, in a list of tuples, ie [[key, value], [key, value]]
		:return: JSON data from the REST API
		"""
		arg_string = ''
		for arg in args:
			arg_string += '&{}={}'.format(arg[0], arg[1])

		ret = requests.get(API_ROOT.format(self.key, method, arg_string))

		return json.loads(ret.content)

	def get_album_info(self, artist, album):
		"""
		Returns the album info from the API
		:param artist:
		:param album:
		:return:
		"""
		return self.request('album.getinfo', [['artist', artist], ['album', album]])

	def get_artist_info(self, artist):
		"""
		Returns artist info
		:param artist:
		:return:
		"""
		return self.request('artist.getinfo', [['artist', artist]])

	def get_similar_artists(self, artist):
		return self.request('artist.getsimilar', [['artist', artist]])

	def get_similar_tracks(self, artist, track):
		return self.request('track.getsimilar', [['artist', artist], ['track', track]])

	def get_similar_tracks_sanitized(self, artist, track):
		"""
		Returns similar tracks as a list of Tracks
		:param artist:
		:param track:
		:return:
		"""
		try:
			return [Track(artist=t['artist']['name'], name=t['name']) for t in self.get_similar_tracks(artist, track)['similartracks']['track']]
		except KeyError:
			# print(artist, track)
			# print(self.get_similar_tracks(artist, track))
			return []

