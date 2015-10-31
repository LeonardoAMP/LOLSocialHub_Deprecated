from django.contrib import admin
from LOLHub import models

class SummonersAdmin(admin.ModelAdmin):
    pass

class StreamersAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Summoners, SummonersAdmin)
admin.site.register(models.Streamers, StreamersAdmin)