# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

urlpatterns = patterns('geocamTalk.views',
    url(r'messages/create', 'create_message',
         name='talk_create_message'),
    url(r'messages/clear', 'clear_messages',
         name='talk_clear_messages'),
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
)
