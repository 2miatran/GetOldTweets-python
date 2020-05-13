import sys
import pandas as pd
import os
import time
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
import codecs

import got3 as got

def printTweet(descr, tweet):
	"""
	Helper function to print tweet
	:param descr:
	:param tweet: a json dictionary for tweet
	:return: None
	"""
	print(descr)
	print("Username: %s" % t.username)
	print("Retweets: %d" % t.retweets)
	print("Text: %s" % t.text)
	print("Mentions: %s" % t.mentions)
	print("Hashtags: %s\n" % t.hashtags)


def receiveBuffer(tweets, outputFile):
	"""

	:param tweets: a tweet in form of dictionary
	:param outputFile: outfile
	:return: None
	"""
	for t in tweets:
		outputFile.write(('\n%s\t%s\t%s\t%s\t%s\t%s\t"%s"\t%s\t%s\t"%s"\t"%s"\t%s\t%s'
						  % (t.username, t.date.strftime("%Y-%m-%d %H:%M"),
							 t.to, t.replies, t.retweets, t.favorites,
							 t.text, t.geo, t.mentions, t.hashtags, t.id,
							 t.permalink, t.expandlink)))

	outputFile.flush()



def TweetColecting(list_of_kw, startdate, enddate, exclude, outfile):
	"""
	Function to parse tweets between period of time based on included/excluded keywords.
	Tweet Manager has been modified to fixed the error of stopping halfway due to time limit exceed
	Current info retrieved including:
	- id
	- text (with emojies)
	- time of tweets
	- user name
	- number of retweets
	- Number of favorites
	- geo location
	- hashtags and mentions
	- replies
	- to
	- permalink (link to tweets)
	- expandlink (linked that was included in tweets, will be www.twitter... with tweets that are retweeted, other domain website or none.)
	- plan: get also the user whose tweet was tweeted / uer


	:param list_of_kw: a list of keywords to search for. The returned tweets will be all that include any of these keywords
	:param startdate: time start of tweets
	:param enddate: time end of tweets
	:param exclude: list of words to be excluded
	:param outfile: the name of the folder to save tweets
	:return: None

	"""
	list_of_kw = [f'"{item}" OR ' for item in list_of_kw]
	keys_to_scrap = [''.join(list_of_kw).strip(" OR ")]
	#print(keys_to_scrap)

	daterange = (pd.date_range(start=startdate, end=enddate, freq='24h'))



	print("\nCollecting tweets by key : ", key)

	for single_date in daterange:

		day_after = single_date + relativedelta(days=1)

		outputFilePath = "./" + outfile + "/"
		outputFileName = str(single_date.strftime("%Y-%m-%d")) + ".csv"

		if not os.path.exists(outfile):
			os.makedirs(outfile)

		print("\nCollecting tweets between", single_date.strftime("%Y-%m-%d"), " to ", day_after.strftime("%Y-%m-%d"), "for", outputFilePath + outputFileName)

		tweetCriteria = (got.manager.TweetCriteria()
						 .setQuerySearch(key)
						 .setSince(single_date.strftime("%Y-%m-%d"))
						 .setUntil(day_after.strftime("%Y-%m-%d")).setLang('en')
						 .setEmoji('named')
						 .setExcludeWords(exclude))

		outputFile = codecs.open(outputFilePath + outputFileName, "a", "utf-8")

		print('Searching...\n')

		tweet = got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer, outputFile)
		time.sleep(2)


if __name__ == '__main__':

	# list_of_kw = ["#gettested", "#stayhome", "#gettested",
	#			  "#wearamask", "#sixfeetapart", "#mask",
	#			  "#socialdistancing", "get tested", "#flattenthecurve"]

	list_of_kw = ["#iamnotavirus", "#hateisavirus"]
	startdate = '02-01-2020'
	enddate = '05-07-2020'
	exclude = ["hiv"]
	outfile = "racism"
	TweetColecting(list_of_kw, startdate, enddate, exclude, outfile)
