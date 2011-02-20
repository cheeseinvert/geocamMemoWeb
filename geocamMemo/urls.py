# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *



urlpatterns = patterns('',
    url(r'messages/create', 'geocamMemo.views.create_message'),
    url(r'messages/(?P<username>[a-zA-Z][a-zA-Z0-9@+.\-]*[a-zA-Z0-9])',
         'geocamMemo.views.message_list_filtered_username'),
    url(r'messages',  'geocamMemo.views.message_list'),  #include('geocamMemo.urls')),
)
