'edit_message'# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

urlpatterns = patterns('geocamMemo.views',
    url(r'messages/create.json', 'create_message_json',
        name='memo_create_message_json'),
    url(r'messages/create', 'create_message',
        name='memo_create_message'),
    url(r'messages/edit/(?P<message_id>\d+)', 'edit_message', 
        name='memo_edit_message'),
    url(r'messages/delete/(?P<message_id>\d+)', 'delete_message', 
        name='memo_delete_message'),
    url(r'messages/details/(?P<message_id>\d+)$', 'message_details', 
        name="memo_message_details"),
    url(r'messages/details/(?P<message_id>\d+).json', 'message_details_json', 
        name="memo_message_details_json"),
    url(r'messages/(?P<author_username>[a-zA-Z][a-zA-Z0-9@+.\-]*[a-zA-Z0-9])', 'message_list', 
        name="memo_message_list_user"),
    url(r'messages.json','message_list_json', 
        name="memo_message_list_all_json"),
    url(r'messages',  'message_list', 
        name="memo_message_list_all"),
    url(r'map', 'message_map', 
        name="memo_message_map"),
)
