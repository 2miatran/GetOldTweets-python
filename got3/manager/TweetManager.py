import urllib.request, urllib.parse, urllib.error,urllib.request,urllib.error,urllib.parse,json,re,datetime,sys,http.cookiejar
from .. import models
from pyquery import PyQuery
import time
countglobal = 0
import re
class TweetManager:
	
	def __init__(self):
		pass
		
	@staticmethod
	def getTweets(tweetCriteria, receiveBuffer=None, outputFile = '', bufferLength=200, proxy=None):
		refreshCursor = ''
	
		results = []
		resultsAux = []
		cookieJar = http.cookiejar.CookieJar()

		active = True

		while active:
			json = TweetManager.getJsonReponse(tweetCriteria, refreshCursor, cookieJar, proxy)
			if len(json['items_html'].strip()) == 0:
				break



			refreshCursor = json['min_position']
			scrapedTweets = PyQuery(json['items_html'])
			#Remove incomplete tweets withheld by Twitter Guidelines
			scrapedTweets.remove('div.withheld-tweet')
			tweets = scrapedTweets('div.js-stream-tweet')
			
			if len(tweets) == 0:
				break
			
			for tweetHTML in tweets:
				tweetPQ = PyQuery(tweetHTML)

				tweet = models.Tweet()

				usernames = tweetPQ("span.username.u-dir b").text().split()
				if not len(usernames):  # fix for issue #13
					continue

				
				#usernameTweet = tweetPQ("span.username.u-dir b").text()  #tweetPQ("span.username.js-action-profile-name b").text()
				#txt = tweetPQ("p.js-tweet-text").text() # re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'))
				retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""))
				favorites = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""))
				
				dateSec = int(tweetPQ("small.time span.js-short-timestamp").attr("data-time"))
				id = tweetPQ.attr("data-tweet-id")
				permalink = tweetPQ.attr("data-permalink-path")
				user_id = int(tweetPQ("a.js-user-profile-link").attr("data-user-id"))
				
				geo = ''
				geoSpan = tweetPQ('span.Tweet-geo')
				if len(geoSpan) > 0:
					geo = geoSpan.attr('title')
				urls = []
				for link in tweetPQ("a"):
					try:
						urls.append((link.attrib["data-expanded-url"]))
					except KeyError:
						pass
				tweet.id = str(id)
				tweet.permalink = 'https://twitter.com' + permalink
				tweet.username = usernames[0]
				# Fine linkout        
				tweet.expandlink = tweetPQ("a.twitter-timeline-link").attr("data-expanded-url")
				#print(tweet.outlink)
				#print(tweetPQ)
				#if str(tweet.id) == '1242601767810019329': print(tweetPQ)
				rawtext = TweetManager.textify(tweetPQ("p.js-tweet-text").html(), tweetCriteria.emoji, tweet.username) 

				tweet.text = " ".join(rawtext.splitlines()).replace('# ', '#').replace('@ ', '@').replace('$ ', '$')
				tweet.date = datetime.datetime.fromtimestamp(dateSec)
#				tweet.formatted_date = datetime.datetime.fromtimestamp(dateSec).strftime("%a %b %d %X +0000 %Y")
				tweet.retweets = retweets
				tweet.favorites = favorites
				tweet.mentions = " ".join(re.compile('(@\\w*)').findall(tweet.text))
				tweet.hashtags = " ".join(re.compile('(#\\w*)').findall(tweet.text))
				tweet.geo = geo
				tweet.urls = ",".join(urls)
				tweet.user_id = user_id
				
				tweet.replies = int(tweetPQ("span.ProfileTweet-action--reply span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""))
				tweet.to = ', '.join(usernames[1:]).rstrip(', ') if len(usernames) >= 2 else None  # take all recipients if many
				#'data-expanded-url'
				results.append(tweet)
				resultsAux.append(tweet)
				
				if receiveBuffer and len(resultsAux) >= bufferLength:
					receiveBuffer(resultsAux, outputFile)
					resultsAux = []
				
				if tweetCriteria.maxTweets > 0 and len(results) >= tweetCriteria.maxTweets:
					active = False
					break
					
		
		if receiveBuffer and len(resultsAux) > 0:
			receiveBuffer(resultsAux, outputFile)
		
		return results

	@staticmethod
	def textify(html, emoji, username):
		"""Given a chunk of text with embedded Twitter HTML markup, replace
		emoji images with appropriate emoji markup, replace links with the original
		URIs, and discard all other markup.
		"""
		# Step 0, compile some convenient regular expressions
		#if username == 'shiblaqbri': print('='*10,username,'='*10)
		imgre = re.compile("^(.*?)(<img.*?/>)(.*)$")
		charre = re.compile("^&#x([^;]+);(.*)$")
		htmlre = re.compile("^(.*?)(<.*?>)(.*)$")
		are = re.compile("^(.*?)(<a href=[^>]+>(.*?)</a>)(.*)$")

		# Step 1, prepare a single-line string for re convenience
		puc = chr(0xE001)
		html = html.replace("\n", puc)

		# Step 2, find images that represent emoji, replace them with the
		# Unicode codepoint of the emoji.
		text = ""
		match = imgre.match(html)
		while match:
				text += match.group(1)
				img = match.group(2)
				html = match.group(3)

				attr = TweetManager.parse_attributes(img)
				if emoji == "unicode":
					chars = attr["alt"]
					match = charre.match(chars)
					while match:
						text += chr(int(match.group(1),16))
						chars = match.group(2)
						match = charre.match(chars)
				elif emoji == "named":
					try:#        
						text += " Emoji[" + attr['title'] + "] "
						#print('====================================yes======================')
						#print("Emoji[" + attr['title'] + "] ")
					except:
						pass #print('====================================No======================')
						#pattern = '.+/(.+)\.\w+$' 
						#text += "Emoji[" + re.findall(pattern, attr['src'])[-1] + "] " 
						#print("Emoji[" + re.findall(pattern, attr['src'])[-1] + "] ")               
				else:
			 		text += " "

				match = imgre.match(html)
		text = text + html

		# Step 3, find links and replace them with the actual URL
		html = text
		text = ""
		match = are.match(html)
		while match:
				text += match.group(1)
				link = match.group(2)
				linktext = match.group(3)
				html = match.group(4)

				attr = TweetManager.parse_attributes(link)
				try:	
			 			if "u-hidden" in attr["class"]:
								pass
			 			elif "data-expanded-url" in attr \
			 			and "twitter-timeline-link" in attr["class"]:
								text += attr['data-expanded-url']
			 			else:
								text += link
				except:
						pass

				match = are.match(html)
		text = text + html
		#print('\n',text)
		# Step 4, discard any other markup that happens to be in the tweet.
		# This makes textify() behave like tweetPQ.text()
		html = text
		text = ""
		match = htmlre.match(html)
		while match:
				text += match.group(1)
				html = match.group(3)
				match = htmlre.match(html)
		text = text + html

		# Step 5, make the string multi-line again.
		text = text.replace(puc, "\n")
		#if username == 'shiblaqbri': print('\n', text)
		return text
   
	@staticmethod
	def parse_attributes(markup):
			"""Given markup that begins with a start tag, parse out the tag name
			and the attributes. Return them in a dictionary.
			"""
			gire = re.compile("^<([^\s]+?)(.*?)>.*")
			attre = re.compile("^.*?([^\s]+?)=\"(.*?)\"(.*)$")
			attr = {}

			match = gire.match(markup)
			if match:
					attr['*tag'] = match.group(1)
					markup = match.group(2)

					match = attre.match(markup)
					while match:
							attr[match.group(1)] = match.group(2)
							markup = match.group(3)
							match = attre.match(markup)

			return attr
	
	@staticmethod
	def getJsonReponse(tweetCriteria, refreshCursor, cookieJar, proxy):
		url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd&%smax_position=%s"
		
		urlGetData = ''
		if hasattr(tweetCriteria, 'username'):
			urlGetData += ' from:' + tweetCriteria.username
			
		if hasattr(tweetCriteria, 'since'):
			urlGetData += ' since:' + tweetCriteria.since
			
		if hasattr(tweetCriteria, 'until'):
			urlGetData += ' until:' + tweetCriteria.until
			
		if hasattr(tweetCriteria, 'querySearch'):
			urlGetData += ' ' + tweetCriteria.querySearch

		if hasattr(tweetCriteria, 'excludeWords'):
				urlGetData += ' -'.join([''] + tweetCriteria.excludeWords)

			
		if hasattr(tweetCriteria, 'lang'):
			urlLang = 'lang=' + tweetCriteria.lang + '&'
		else:
			urlLang = ''
		url = url % (urllib.parse.quote(urlGetData), urlLang, refreshCursor)
		#print(url)

		headers = [
			('Host', "twitter.com"),
			('User-Agent', "Mozilla/8.0 (Windows NT 6.1; Win64; x64)"),
			('Accept', "application/json, text/javascript, */*; q=0.01"),
			('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
			('X-Requested-With', "XMLHttpRequest"),
			('Referer', url),
			('Connection', "keep-alive")
		]

		if proxy:
			opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': proxy, 'https': proxy}), urllib.request.HTTPCookieProcessor(cookieJar))
		else:
			opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
		opener.addheaders = headers

		keeptrying = True
		second = 600 # 6 minutes 
		  
		while keeptrying:
				
			second = second - 300
			if second <= 0: second = 60   
				
			try:
					#print(url)
			  response = opener.open(url)
			  jsonResponse = response.read()
			  print(f"Last cursor ended at {refreshCursor}", end="\r")#, flush = True)
			  keeptrying = False
			  #print('keeptrying set to false, continue with new data')
			
			except:
			  print('\n')			  
			  print(f"Rate limit exceeded, sleep for {second}!...") #. Try to see on browser: https://twitter.com/search?q=%s&src=typd" % urllib.parse.quote(urlGetData))
				  
			  time.sleep(second)

		  
			#print("Unexpected error:", sys.exc_info()) #[0])
			#sys.exit()
			#return #jsonResponse
		#print('\n')
		dataJson = json.loads(jsonResponse.decode())
		
		return dataJson		
