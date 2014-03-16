# Import Models
from grain.models import GrainVacuum, TwitterProfile, Alert, Config
from django.contrib.auth.models import User

# import everything else
from twython import Twython
import datetime
import threading
from send_email import SendEmail
from nexmomessage import NexmoMessage
from send_text import SendText
import json

import string
import re


# Connect to Redis
from rq import Connection, Queue
from redis import Redis
redis_conn = Redis('localhost',6379)

# Pulls Tweets from Twitter API via Twython
def GetTweets(APP_KEY,APP_SECRET,OAUTH_TOKEN,OAUTH_TOKEN_SECRET,follow_user,key_words,last_id,grain_id,profile):
	# Connect to Twitter via Twython
	twitter = Twython(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	error = None
	created_at_final = None

	try:
		# check if any tweet has been checked yet
		if last_id == None or last_id == "":
			timeline = twitter.get_user_timeline(screen_name=follow_user,count=1) # Get the most recent Tweet
			print last_id
			LookForGrains(timeline,key_words,grain_id,follow_user,profile)
		else:
			# If this is not the First Tweet checked, set last_id to the last Tweet ID in the group of tweets and proceed
			print last_id
			timeline = twitter.get_user_timeline(screen_name=follow_user,since_id=last_id) # Get all Tweets since last_id Tweet
			if len(timeline) > 0:
				if last_id != timeline[-1]['id_str']:
					LookForGrains(timeline,key_words,grain_id,follow_user,profile)
		
	except Exception as error:
		if error == "Not authorized.":
			print 'Unable to read that persons Tweets'
		print error
	
# Function used to Extract Hashtags and put into list
def extract_hash_tags(s):
	return set(part[1:] for part in s.split() if part.startswith('#'))

# Compare the Tweets with the Alerts that have been set
def LookForGrains(timeline,key_words,grain_id,follow_user,profile):
	key_words = [x.lower() for x in key_words] # Set keywords to all lowercase
	
	grain = GrainVacuum.objects.all().filter(id=grain_id).get()
	alerts = grain.alerts
	
	if len(timeline) > 0:
		for tweet in timeline:
				
			tweet_string = (tweet['text'].encode('ascii', 'ignore')) # Encode the tweet into ascii
			tweet_text = tweet_string.lower() # Change tweet to all lower case
			tweet_text = re.sub('\,',' ', tweet_text) # Remove all commas
			
			hashtags = extract_hash_tags(tweet_text) # breaks hastags up into list
			matching_words = [] # stores what ever words matched
			matching_tweet = False

			# Search through Hashtags for specific words
			for tag in hashtags:
				if any(word in tag for word in key_words):
					matching_tweet = True
				
					for key in key_words:
						if key in tag:
							matching_words.append(key) # If Match add to List
				
			# Search for single word in Tweet String ; break stirng into list
			print tweet_text.split()
			if any(word in tweet_text.split() for word in key_words):
				matching_tweet = True
				
				for key in key_words:
					if key in tweet_text:
						matching_words.append(key) # If Match add to List
						
			# If the word exsits in the Tweet at all
			if any(word in tweet_text for word in key_words):
				matching_tweet = True
				
				for key in key_words:
					if key in tweet_text:
						matching_words.append(key) # If Match add to List
			
			
			#### If TWEET MATCHES --- >> ####
			if matching_tweet == True:
				print 'Matching Tweet::'
				print tweet_string
				print matching_words
				
				# It's a matching Tweet Update Profile and Other Objects
				user = grain.user
				
				email_alert = profile.email_alert # Email Alert Setting (True/False)
				sms_alert = profile.sms_alert # SMS Alert Setting (True/False)
				phone = profile.phone # Phone Number
				alert_type = "standard"
				
				# Determine the Alert Type
				if email_alert == True and sms_alert == True:
					alert_type = "email sms"
				elif email_alert == True:
					alert_type = "email"
				elif sms_alert == True:
					alert_type = "sms"
					
				new_alert = Alert(profile=profile,user=user,grain=grain,message=tweet_string,alert_type=alert_type)
				new_alert.save()
				
				alerts += 1
				
				print 'SMS Alert ' + str(sms_alert)
				
				# If User Wants Email Alert
				if email_alert == True:
				
					# Add Tweet to email Queue
					q_email = Queue('email',connection=redis_conn)
					email_job = q_email.enqueue(SendEmail, follow_user,tweet_string,profile)
					
				# If User Wants SMS Alert
				if (sms_alert == True) and (phone != None or phone != ""): 
				
					# Add Tweet to sms Queue
					q_sms = Queue('sms',connection=redis_conn)
					sms_job = q_sms.enqueue(SendText, follow_user,tweet_string,phone)
			
		new_last_id = timeline[-1]['id_str']
		
		grain_item = GrainVacuum.objects.all().filter(id=grain_id)
		grain_item.update(last_id=new_last_id,alerts=alerts)
		
