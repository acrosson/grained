# Create your views here.
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf

from twython import Twython
from tweetgrain import settings
from grain.models import TwitterProfile,GrainVacuum,Alert,FriendList,Config
import datetime, pytz

def main(request):
	return render_to_response('index.html', context_instance=RequestContext(request))
	
def twitter_login(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/dashboard/')
		
	# Twitter Settings
		
	APP_KEY = Config.objects.all().latest('id').twitter_key
	APP_SECRET = Config.objects.all().latest('id').twitter_secret
	
	twitter = Twython(APP_KEY, APP_SECRET)
	
	auth_props = twitter.get_authentication_tokens(callback_url='http://127.0.0.1:8000/twitter/callback/')
	request.session['request_token'] = auth_props
	return HttpResponseRedirect(auth_props['auth_url'])


def twitter_callback(request, redirect_url='/private'):
	try:
		oauth_verifier = request.GET['oauth_verifier']
	except:
		return HttpResponseRedirect('/')
	
	twitter_token = Config.objects.all().latest('id').twitter_key
	twitter_secret = Config.objects.all().latest('id').twitter_secret
	oauth_token = request.session['request_token']['oauth_token']
	oauth_token_secret = request.session['request_token']['oauth_token_secret']
	    
	twitter = Twython(twitter_token,twitter_secret,oauth_token,oauth_token_secret)
	
	authorized_tokens = twitter.get_authorized_tokens(oauth_verifier)
	print authorized_tokens
	
	try:
		profile = TwitterProfile.objects.get(tw_user_id=authorized_tokens['user_id'])
		user = User.objects.get(pk=profile.user_id)
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		
		oauth_token = authorized_tokens['oauth_token']
		oauth_token_secret = authorized_tokens['oauth_token_secret']
		
		if user.is_active:
			tw_profile = TwitterProfile.objects.all().filter(screen_name=authorized_tokens['screen_name'])
			tw_profile.update(oauth_token=oauth_token,oauth_secret=oauth_token_secret)
			
			login(request, user)
			
			return HttpResponseRedirect('/dashboard/')
		else:
			# failed back to login
			return HttpResponseRedirect('/')
			
	except Exception as error: #TwitterProfile.DoesNotExist
		print error
		
		user_id = authorized_tokens['user_id']
		screen_name = authorized_tokens['screen_name']
		oauth_token = authorized_tokens['oauth_token']
		oauth_token_secret = authorized_tokens['oauth_token_secret']
		
		user = User.objects.create_user(user_id,'',oauth_token_secret)
		
		user = authenticate(username=user_id, password=oauth_token_secret)
		login(request, user)
		
		user_obj = User.objects.all().filter(username=user_id).get()
		
		# Add to TwitterProfile
		profile = TwitterProfile(user=user_obj,oauth_token=oauth_token,oauth_secret=oauth_token_secret,screen_name=screen_name,tw_user_id=user_id)
		profile.save()
		return HttpResponseRedirect('/finish-signup/')
		
	return HttpResponseRedirect('/dashboard/')
	
	
def site_logout(request):

	pass
	
def dashboard(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/')
		
	user = request.user
	profile = TwitterProfile.objects.all().filter(user=user).get()
	grains = GrainVacuum.objects.all().filter(profile=profile)
	
	grain_objects = []
	user_list = []
	word_list = []
	alert_list = []
	id_list = []
	word_string = []
	for grain_item in grains:
		print grain_item
		user_list.append(grain_item.follow_user)
		word_list.append(grain_item.key_words.split(','))
		alert_list.append(grain_item.alerts)
		id_list.append(grain_item.id)
		word_string.append(grain_item.key_words)
		
	grain_objects = zip(user_list,word_list,alert_list,id_list,word_string)
	print grain_objects
	
	# Check if Phone # or Email has been entered
	account_linked = True
	phone = profile.phone
	email = profile.email
	
	if (phone == None or phone == '') and (email == None or email == ''):
		account_linked = None
	
	
	return render_to_response('dashboard.html', {
		'grain_objects': grain_objects,
		'account_linked': account_linked,
	})
	
def add_alert(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/')
		
	context = {}
	context.update(csrf(request))
	
	user = request.user
	profile = TwitterProfile.objects.all().filter(user=user).get()
	
	alerts_count = len(GrainVacuum.objects.all().filter(profile=profile))
	
	screen_name_list = None
	name_list = None
	
	if request.method == "POST":
		follow_user = request.POST['follow_user']
		key_words = request.POST['key_words_list']
		
		follow_user = follow_user.replace('@','')
		
		new_grain = GrainVacuum(profile=profile,user=user,follow_user=follow_user,key_words=key_words)
		new_grain.save()
		
		return HttpResponseRedirect('/dashboard/')
	else:
		# Update FriendList
		
		try:
			# Determine if friend_list exists
			try:
				friend_list = FriendList.objects.all().filter(twitter_profile=profile).get()
			except:
				# if it doesn't exist create a blank one
				
				new_friend_list = FriendList(twitter_profile=profile)
				new_friend_list.save()
				friend_list = FriendList.objects.all().filter(twitter_profile=profile).get()
			
			est = pytz.timezone('US/Eastern') # Eastern Time Zone
			last_checked = friend_list.last_checked
			now = datetime.datetime.now()
			tdelta = 0
			if last_checked != None:
				last_checked = last_checked.astimezone(est).replace(tzinfo=None)
				tdelta = int((now - last_checked).total_seconds() / 60)
			
			print last_checked
			
			if tdelta > 15 or last_checked == None:
				APP_KEY = Config.objects.all().latest('id').twitter_key
				APP_SECRET = Config.objects.all().latest('id').twitter_secret
				
				# Get Authorization Credentials
				OAUTH_TOKEN = profile.oauth_token
				OAUTH_TOKEN_SECRET = profile.oauth_secret
				
				friend_list_update = FriendList.objects.all().filter(twitter_profile=profile)
				twitter = Twython(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
				
				# Query Twitter Friends List API until none
				screen_name_list = ""
				name_list = ""
				next_cursor=-1
				count = 0
				while next_cursor:
					follow_list = twitter.get_friends_list(count=200,cursor=next_cursor)
					
					y = 0
					for user in follow_list['users']:
						screen_name = user['screen_name']
						name = user['name']
						
						if y == 0:
							screen_name_list += screen_name
							name_list += name
						else:
							screen_name_list += "," + screen_name
							name_list += "," + name
						
						y += 1
						print screen_name + ' ' + name
						
					count += 1
					if count == 15 or next_cursor == 0:
						break
					next_cursor = follow_list["next_cursor"]
					
				friend_list_update.update(last_checked=now,name=name_list,handle=screen_name_list)
			else:
				screen_name_list = friend_list.handle
				name_list = friend_list.name
				
		except Exception as error:
			print error
	
	return render_to_response('add_alert.html', {'screen_name_list':screen_name_list,'name_list':name_list,'alerts_count':alerts_count}, context_instance=RequestContext(request))
	
def remove_user(request,follow_user):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/')
		
	user = request.user
	profile = TwitterProfile.objects.all().filter(user=user).get()
	try:
		grain = GrainVacuum.objects.all().filter(profile=profile,follow_user=follow_user).get()
	except:
		follow_user = None
		
	return render_to_response('remove_user.html', {'follow_user':follow_user},context_instance=RequestContext(request))
	
def settings(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/')
		
	user = request.user
	profile = TwitterProfile.objects.all().filter(user=user).get()
	email_alert = profile.email_alert
	sms_alert = profile.sms_alert
	phone = profile.phone
	email = profile.email
	
	return render_to_response('settings.html', {'email_alert':email_alert,'sms_alert':sms_alert,'phone':phone,'email':email}, context_instance=RequestContext(request))
	
def edit_user(request,follow_user):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/')
		
		
	user = request.user
	profile = TwitterProfile.objects.all().filter(user=user).get()
	grain = GrainVacuum.objects.all().filter(profile=profile,follow_user=follow_user).get()
	key_words = grain.key_words
	
	return render_to_response('edit_alert.html', {'follow_user':follow_user,'key_words':key_words},context_instance=RequestContext(request))
	
def complete_reg(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/')
		
	user = request.user
	profile = TwitterProfile.objects.all().filter(user=user).get()
	email_alert = profile.email_alert
	sms_alert = profile.sms_alert
	phone = profile.phone
	email = profile.email
	completed_signup = profile.completed_signup
	
	if (completed_signup == True):
		return HttpResponseRedirect('/dashboard/')
	
	return render_to_response('complete_reg.html', {'email_alert':email_alert,'sms_alert':sms_alert,'phone':phone,'email':email}, context_instance=RequestContext(request))
	
def view_alerts(request,follow_user):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/')
		
	user = request.user
	profile = TwitterProfile.objects.all().filter(user=user).get()
	grain = GrainVacuum.objects.all().filter(profile=profile,follow_user=follow_user)
	alerts = Alert.objects.all().filter(profile=profile,grain=grain).order_by('timestamp').reverse()

	return render_to_response('view_alerts.html', {'alerts':alerts,'follow_user':follow_user}, context_instance=RequestContext(request))
	
def page_not_found_custom(request):

	return render_to_response('404.html')
	
def page_error_found_custom(request):

	return render_to_response('500.html')