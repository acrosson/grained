from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from django.db.models import Count

from grain.models import TwitterProfile,GrainVacuum,Alert,FriendList,Config

def view_alerts(request):
	if not request.user.is_superuser:
		return HttpResponseRedirect('/dashboard')
		
	alerts = Alert.objects.all().order_by('timestamp').reverse()[:30] # Get the most recent 30 alerts

	return render_to_response('stats_view_alerts.html', {'alerts':alerts}, context_instance=RequestContext(request))