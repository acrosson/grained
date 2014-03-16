from django.utils import simplejson
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
import datetime

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

from dajaxice.utils import deserialize_form

from grain.models import TwitterProfile,GrainVacuum

import json
import urllib
import re

def validateEmail(email):
	from django.core.validators import validate_email
	from django.core.exceptions import ValidationError
	try:
		validate_email( email )
		return True
	except ValidationError:
		return False
		
    
@dajaxice_register
def add_alert(request,follow_user,key_words):
	dajax = Dajax()
	
	follow_user = follow_user.replace('@','')
	follow_user = follow_user.replace(' ','')
	
	user = request.user
	
	profile = TwitterProfile.objects.all().filter(user=user).get()
	grains = GrainVacuum.objects.all().filter(user=user,profile=profile)
	
	user_list = []
	for grain in grains:
		user_list.append(grain.follow_user)
		
	if follow_user in user_list:
		dajax.assign('#status', 'innerHTML', '<div class="error">You already have an alert for @'+follow_user+'</div>')
	else:
		new_grain = GrainVacuum(user=user,follow_user=follow_user,key_words=key_words,profile=profile)
		new_grain.save()
	
		dajax.assign('#block', 'innerHTML', '<div class="success">Alert for @'+follow_user+' has been added</div><p>Visit the Dashboard to see your current alert list</p>')
	
	return dajax.json()


@dajaxice_register
def edit_alert(request,follow_user,key_words):
	dajax = Dajax()
	
	user = request.user
	profile = TwitterProfile.objects.all().filter(user=user).get()
	try:
		grain = GrainVacuum.objects.all().filter(user=user,profile=profile,follow_user=follow_user)
		grain.update(key_words=key_words)
		dajax.assign('#status_'+follow_user, 'innerHTML', '<div class="success">Alert Updated</div>')
	except:
		dajax.assign('#status_'+follow_user, 'innerHTML', '<div class="error">Something went wrong. Try again.</div>')
		print error
	
	return dajax.json()
	
@dajaxice_register
def remove_alert(request,follow_user):
	dajax = Dajax()
	
	user = request.user
	profile = TwitterProfile.objects.all().filter(user=user).get()
	try:
		grain = GrainVacuum.objects.all().filter(user=user,profile=profile,follow_user=follow_user).get()
		grain.delete()
		
		dajax.assign('#block', 'innerHTML', '<div class="success">Alert for @'+follow_user+' has been added</div><p>Visit the Dashboard to see your current alert list</p>')
	except:
		dajax.assign('#status', 'innerHTML', '<div class="error">Alert for @'+follow_user+' has been removed.</div>')
	
	return dajax.json()
	
@dajaxice_register
def update_settings(request,email,sms,phone,email_address,form_type):
	dajax = Dajax()
	
	if email == 'on':
		email = True
	else:
		email = False
	
	if sms == 'on':
		sms = True
	else:
		sms = False
		
	# Validate Phone #
	if sms == True:
		reg_letters = re.search('[a-zA-Z]+',phone)
		if reg_letters != None:
			dajax.assign('#status', 'innerHTML', '<div class="error">Use correct Phone # format.</div>')
			
			return dajax.json()
		try:
			int(phone)
			if len(phone) != 10:
				dajax.assign('#status', 'innerHTML', '<div class="error">Use a 10 digit, US phone #.</div>')
				return dajax.json()
		except:
			dajax.assign('#status', 'innerHTML', '<div class="error">Use correct Phone # format.</div>')
			
			return dajax.json()
	else:
		phone = ''
		
	# Validate Email
	if email == True:
		email_validation = validateEmail(email_address)
		if email_validation == False:
			dajax.assign('#status', 'innerHTML', '<div class="error">Enter a valid Email.</div>')
			
			return dajax.json()
	
	user = request.user
	try:
		profile = TwitterProfile.objects.all().filter(user=user)
		profile.update(email_alert=email,sms_alert=sms,phone=phone,email=email_address)
		dajax.assign('#status', 'innerHTML', '<div class="success">Settings Updated!</div>')
		
		if form_type == 'finish':
			profile.update(completed_signup=True)
			dajax.redirect('/dashboard/', delay=100)
			return dajax.json()
			
	except Exception as error:
		dajax.assign('#status', 'innerHTML', '<div class="error">Something went wrong. Try again.</div>')
		print error
	
	return dajax.json()