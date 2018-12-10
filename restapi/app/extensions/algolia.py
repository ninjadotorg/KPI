from datetime import datetime
from algoliasearch import algoliasearch
from app.helpers.utils import local_to_utc

class Algolia(object):
	def __init__(self, app=None):
		super(Algolia, self).__init__()
		if app:
			self.app = app
			self.load_algolia()


	def init_app(self, app):
		self.app = app
		self.load_algolia()


	def load_algolia(self):
		client = algoliasearch.Client(self.app.config['ALGOLIA_APPLICATION_ID'], self.app.config['ALGOLIA_API_KEY'])
		self.index = client.init_index(self.app.config['ALGOLIA_INDEX_NAME'])
		self.index.set_settings({
			'searchableAttributes': [
				'eventName, sourceName',
				'sourceURL'
			]
		})


	def search(self, text):
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)
		return self.index.search(text, {"filters": "closingTime > {}".format(seconds)})
