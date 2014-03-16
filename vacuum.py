# Import Django Settings
from django.core.management import setup_environ
from tweetgrain import settings
setup_environ(settings)

# Import Models
from grain.models import GrainVacuum, TwitterProfile, Alert, Config
from django.contrib.auth.models import User

# import everything else
from twython import Twython
import datetime

import pytz
from django.core.cache import cache # This is the memcache cache.
from time import sleep

from get_tweets import GetTweets

# Ignore Runtime Warnings for output
import warnings
warnings.simplefilter("ignore", RuntimeWarning) 
from django.db import connection

APP_KEY = Config.objects.all().latest('id').twitter_key
APP_SECRET = Config.objects.all().latest('id').twitter_secret

# Connect to Redis
from rq import Connection, Queue
from redis import Redis
redis_conn = Redis('localhost',6379)
q = Queue('tweet',connection=redis_conn)  # no args implies the default queue


def ConvertTime(created_at):
	# Localize Tweet datetime and convert to UTC
	local = pytz.timezone ('America/New_York')
	local_dt = local.localize(created_at, is_dst=None)
	created_at_final = local_dt.astimezone (pytz.utc).replace(tzinfo=None)
	
	return created_at_final
	
from django.db import transaction

@transaction.commit_manually
def flush_transaction():
	"""
	Flush the current transaction so we don't read stale data
	
	Use in long running processes to make sure fresh data is read from
	the database.  This is a problem with MySQL and the default
	transaction mode.  You can fix it by setting
	"transaction-isolation = READ-COMMITTED" in my.cnf or by calling
	this function at the appropriate moment
	"""
	transaction.commit()
	
def PushToQueue(grain_item):
	follow_user = grain_item.follow_user
	key_words = grain_item.key_words.split(',')
	grain_id = grain_item.id
	last_id = grain_item.last_id
	profile = grain_item.profile
	
	OAUTH_TOKEN = profile.oauth_token
	OAUTH_TOKEN_SECRET = profile.oauth_secret
	
	current_dt = datetime.datetime.now()
	
	# Update last_checked in Model
	grain_item = GrainVacuum.objects.all().filter(id=grain_id)
	grain_item.update(last_checked=current_dt)
	
	job = q.enqueue(GetTweets, APP_KEY,APP_SECRET,OAUTH_TOKEN,OAUTH_TOKEN_SECRET,follow_user,key_words,last_id,grain_id,profile)
    
def GetAlerts():
	cache.clear() # Clear Cache
	flush_transaction()
	connection.queries = [] # Clear user creation queries
	
	try:
		# Get All Alerts that haven't been checked in a minute or so
		one_minute_ago = datetime.datetime.now() - datetime.timedelta(minutes=1)
		
		desired_grains = GrainVacuum.objects.all().filter(last_checked__lte=one_minute_ago)
		if desired_grains:
			print desired_grains
		
		for grain_item in desired_grains:
			PushToQueue(grain_item)
			
		# Get All Alerts that haven't been checked at all
		new_grains = GrainVacuum.objects.all().filter(last_checked=None)
		if new_grains:
			print new_grains
		
		for grain_item in new_grains:
			PushToQueue(grain_item)
	except Exception as error:
		print error
	
if __name__ == "__main__":
	
	while True:

		GetAlerts()
		
		sleep(0.1)