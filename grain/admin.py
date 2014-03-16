from grain.models import GrainVacuum, TwitterProfile, Alert, FriendList, Config
from django.contrib import admin

class GrainVacuumAdmin(admin.ModelAdmin):
	pass
	
class TwitterProfileAdmin(admin.ModelAdmin):
	pass
	
class AlertAdmin(admin.ModelAdmin):
	pass
	
class FriendListAdmin(admin.ModelAdmin):
	pass
	
class ConfigAdmin(admin.ModelAdmin):
	pass

admin.site.register(GrainVacuum, GrainVacuumAdmin)
admin.site.register(TwitterProfile,TwitterProfileAdmin)
admin.site.register(Alert,AlertAdmin)
admin.site.register(FriendList,FriendListAdmin)
admin.site.register(Config,ConfigAdmin)