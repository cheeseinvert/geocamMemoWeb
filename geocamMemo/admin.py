# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.contrib import admin
from geocamMemo.models import GeocamMessage
from django.contrib import admin

class GeocamMessageAdmin(admin.ModelAdmin):
    list_display = ('author', 
                    'content', 
                    'lat', 
                    'lon')
    list_filter = ['author']

admin.site.register(GeocamMessage, GeocamMessageAdmin)

