# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

urlpatterns = patterns('geocamTalk.views',
    url(r'register$', 'register',
         name='talk_register_c2dm'),
    url(r'unregister$', 'unregister',
         name='talk_unregister_c2dm'),
    url(r'messages/create.json', 'create_message_json',
         name='talk_create_message_json'),
    url(r'messages/create', 'create_message',
         name='talk_create_message'),
    url(r'messages/clear', 'clear_messages',
         name='talk_clear_messages'),
    url(r'messages/details/(?P<message_id>\d+).json', 'message_details_json', 
        name="talk_message_details_json"),
    url(r'messages/details/(?P<message_id>\d+)$', 'message_details', 
        name="talk_message_details"),
    url(r'messages/(?P<recipient_username>[^ ]+)/(?P<author_username>[^ ]+).json', 'feed_messages',
         name="talk_message_list_to_from_json"),
    url(r'messages/(?P<recipient_username>[^ ]+).json', 'feed_messages',
         name="talk_message_list_author_json"),
    url(r'messages.json', 'feed_messages',
         name="talk_message_list_all_json"),
    url(r'messages/(?P<recipient_username>[^ ]+)/(?P<author_username>[^ ]+)', 'message_list',
         name="talk_message_list_to_from"),
    url(r'messages/(?P<recipient_username>[^ ]+)', 'message_list',
         name="talk_message_list_author"),
    url(r'messages',  'message_list',
         name="talk_message_list_all"),
    url(r'map', 'message_map', 
        name="talk_message_map"),
)
