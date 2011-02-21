# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

urlpatterns = patterns('geocamTalk.views',
    url(r'messages/create', 'create_message'),
    url(r'messages',  'message_list'),
)
