# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.contrib import admin
from geocamTalk.models import TalkMessage
from geocamTalk.models import TalkUserProfile
from django.contrib import admin

class TalkMessageAdmin(admin.ModelAdmin):
    list_display = ('author', 
                    'content',
                    'content_timestamp', 
                    'latitude', 
                    'longitude',
                    'altitude',
                    'accuracy',
                    'heading',
                    'speed',
                    'position_timestamp' )
    list_filter = ['author']

admin.site.register(TalkMessage, TalkMessageAdmin)
admin.site.register(TalkUserProfile)

