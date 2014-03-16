from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

handler404 = 'grain.views.page_not_found_custom'  
handler500 = 'grain.views.page_error_found_custom'

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'grain.views.main', name='home'),
    
    url(
        r'^twitter/login/$', 
        'grain.views.twitter_login', 
        name="twitter_login"
    ),

    url(r'^twitter/callback/$', 
        'grain.views.twitter_callback', 
        name="twitter_callback"
    ),   

    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

	url(r'^dashboard/$', 'grain.views.dashboard'),
	url(r'^add/$', 'grain.views.add_alert'),
    url(r'^remove/(?P<follow_user>\w+)/$','grain.views.remove_user'),
    url(r'^edit/(?P<follow_user>\w+)/$','grain.views.edit_user'),
	url(r'^settings/$', 'grain.views.settings'),
	url(r'^finish-signup/$', 'grain.views.complete_reg'),
    url(r'^view-alerts/(?P<follow_user>\w+)/$','grain.views.view_alerts'),
	
	# Stats Website
	url(r'^stats/alerts/$', 'statistics.views.view_alerts'),
	    
	url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    # url(r'^tweetgrain/', include('tweetgrain.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
