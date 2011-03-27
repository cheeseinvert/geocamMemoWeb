# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

urlpatterns = patterns('geocamTalk.views',
    url(r'messages/create', 'create_message'),
    url(r'messages/(?P<recipient_username>[^ ]+)/(?P<author_username>[^ ]+)', 'message_list'),
    url(r'messages/(?P<recipient_username>[^ ]+)', 'message_list'),
    url(r'messages',  'message_list'),
    url(r'messagefeed/(?P<recipient_username>[^ ]+)/(?P<author_username>[^ ]+)', 'feed_messages'),
    url(r'messagefeed/(?P<recipient_username>[^ ]+)', 'feed_messages'),
    url(r'messagefeed', 'feed_messages'),
    url(r'messagefeedcnt', 'feed_messages_cnt')
)
