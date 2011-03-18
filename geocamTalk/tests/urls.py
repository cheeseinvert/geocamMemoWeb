# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from geocamTalk.models import TalkMessage
from geocamMemo.models import get_latest_message_revisions
import json

class GeocamTestUrls(TestCase):
    fixtures = ['demoUsers.json', 'demoTalkMessages.json']
    
    def testMessageListUrl(self):
        #arrange
        path = "/talk/messages/"   
        template = "geocamTalk/messagelist.html"

        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)
        
    def testMyMessageListUrl(self):
        me = User.objects.all()[0]
        #arrange
        path = "/talk/messages/%s" % me.username   
        template = "geocamTalk/messagelist.html"

        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)
   
    def testMessageCreateUrl(self):
        #arrange
        path = "/talk/messages/create"
        template = "geocamTalk/message_form.html"

        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)
    
    def testMessageJSONFeedUrl(self):
        #arrange
        path = "/memo/messagefeed"
        
        #act
        guestResponse = self.getResponse(path)
        self.login();
        memberResponse = self.getResponse(path)
        
        #assert
        self.assertEqual(302, guestResponse.status_code, "should redirect if not logged in")
        self.assertEqual(200, memberResponse.status_code, "should display if logged in")

    def testMyMessageJSONFeedUrl(self):
        #arrange
        me = User.objects.all()[0]
        path = "/memo/messagefeed/%s" % me.username   
        
        #act
        guestResponse = self.getResponse(path)
        self.login();
        memberResponse = self.getResponse(path)
        
        #assert
        self.assertEqual(302, guestResponse.status_code, "should redirect if not logged in")
        self.assertEqual(200, memberResponse.status_code, "should display if logged in")
    
    def assertPathRequiresLoginAndUsesTemplate(self, path, template):
        #act
        guestResponse = self.getResponse(path)
        self.login();
        memberResponse = self.getResponse(path)
        
        #assert
        self.assertEqual(302, guestResponse.status_code, "should redirect if not logged in")
        self.assertEqual(200, memberResponse.status_code, "should display if logged in")
        self.assertTemplateUsed(memberResponse, template)
        
    def getResponse(self, path):
        return self.client.get(path)
    def login(self):
        return self.client.login(username = "rhornsby", password = "geocam")