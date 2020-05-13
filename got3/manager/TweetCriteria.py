class TweetCriteria:

	def __init__(self):
		self.maxTweets = 0

	def setUsername(self, username):
		self.username = username
		return self

	def setSince(self, since):
		self.since = since
		return self

	def setUntil(self, until):
		self.until = until
		return self

	def setQuerySearch(self, querySearch):
		self.querySearch = querySearch
		return self

	def setMaxTweets(self, maxTweets):
		self.maxTweets = maxTweets
		return self

	def setLang(self, Lang):
		self.lang = Lang
		return self

	def setTopTweets(self, topTweets):
 		self.topTweets = topTweets
 		return self
	def setEmoji(self, Emoji):
		"""Set emoji style. Style must be one of 'ignore', 'unicode', or 'name'.
		Parameters
		----------
		Emoji : str
		"""
		self.emoji = Emoji
		return self
   
	def setExcludeWords(self, excludeWords):
		"""Set word(s) to exclude from tweets
		Parameters
		----------
		excludeWords : list or iterable
		Example: ["red", "blue", "yellow", "green"]
		"""
		self.excludeWords = excludeWords
		return self