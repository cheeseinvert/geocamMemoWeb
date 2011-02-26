# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *



urlpatterns = patterns('geocamMemo.views',
    url(r'messages/create', 'create_message'),
    url(r'messages/edit/(?P<message_pk>\d+)', 'edit_message'),
    url(r'messages/delete/(?P<message_pk>\d+)', 'delete_message'),
    url(r'messages/(?P<username>[a-zA-Z][a-zA-Z0-9@+.\-]*[a-zA-Z0-9])',
         'message_list_filtered_username'),
    url(r'messages',  'message_list'),  #include('geocamMemo.urls')),
)
