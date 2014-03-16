from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class TwitterProfile(models.Model):
	user = models.ForeignKey(User)
	oauth_token = models.CharField(max_length=200)
	oauth_secret = models.CharField(max_length=200)
	screen_name = models.CharField(max_length=50,blank=True, null=True)
	tw_user_id = models.CharField(max_length=200)
	email = models.EmailField(default='',blank=True,null=True)
	email_alert = models.BooleanField(default=True)
	sms_alert = models.BooleanField(default=True)
	phone = models.CharField(max_length=15,blank=True,null=True)
	
	completed_signup = models.BooleanField(default=False)
	
	def __unicode__(self):
		return ' '.join([
			str(self.screen_name),
		])

class GrainVacuum(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	profile = models.ForeignKey(TwitterProfile,null=True)
	user = models.ForeignKey(User)
	follow_user = models.CharField(max_length=300)
	key_words = models.CharField(max_length=500)
	last_checked = models.DateTimeField(null=True,blank=True)
	last_id = models.CharField(max_length=100,null=True,blank=True)
	alerts = models.IntegerField(default=0)
	
	def __unicode__(self):
		return ' '.join([
			str(self.profile),
			str(self.follow_user),
		])
		
class Alert(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	profile = models.ForeignKey(TwitterProfile,null=True)
	user = models.ForeignKey(User)
	grain = models.ForeignKey(GrainVacuum)
	message = models.CharField(max_length=300)
	ATYPES = (("email", "Email"), ("sms", "SMS"), ("email sms", "Email+SMS"), ("standard","Standard"))
	alert_type = models.CharField(max_length=5, choices=ATYPES, default="standard")
	
	def __unicode__(self):
		return ' '.join([
			str(self.grain),
			str(self.message),
		])
		
class FriendList(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True,null=True,default=None)
	twitter_profile = models.ForeignKey(TwitterProfile)
	name = models.CharField(max_length=200)
	handle = models.CharField(max_length=200)
	last_checked = models.DateTimeField(null=True,blank=True)
	
	def __unicode__(self):
		return ' '.join([
			str(self.twitter_profile),
			str(self.handle),
		])
		
class Config(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True,null=True,default=None)
	twitter_key = models.CharField(max_length=200)
	twitter_secret = models.CharField(max_length=200)
	support_email = models.CharField(max_length=100)
	support_email_pass = models.CharField(max_length=100)
	nexmo_key = models.CharField(max_length=100)
	nexmo_secret = models.CharField(max_length=100)
	nexmo_number = models.CharField(max_length=15,default="")
	
	def __unicode__(self):
		return ' '.join([
			str(self.twitter_key),
			str(self.twitter_secret),
			str(self.support_email),
			str(self.support_email_pass),
		])