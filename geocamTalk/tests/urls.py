# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from geocamTalk.models import TalkMessage
import json

class GeocamTestUrls(TestCase):
    fixtures = ['demoUsers.json', 'demoTalkMessages.json']
    
    def testMessageListUrl(self):
        #arrange
        path = "/talk/messages/"   
        template = "geocamTalk/message_list.html"

        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)
        
    def testMyMessageListUrl(self):
        me = User.objects.all()[0]
        #arrange
        path = "/talk/messages/%s" % me.username   
        template = "geocamTalk/message_list.html"

        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)
        
    def testMessageCreateJSONFeed(self):
        #arrange
        path = "/talk/messages/create.json"

        #act
        guestResponse = self.client.post(path, {})
                 
        #assert    
        self.assertEqual(403, guestResponse.status_code, "Unauthorized access if not logged in")

    def testMessageJsonUrl(self):
        #arrange
        pk = str(TalkMessage.latest.all()[0].pk)
        path = "/talk/messages/details/" + pk + ".json"
        self.login()
        
        #act
        memberResponse = self.getResponse(path)
        
        #assert
        self.assertEqual(200, memberResponse.status_code, "should display single message")  
  
    def testClearMyMessageCount(self):
        #arrange
        me = User.objects.all()[0]
        path = "/talk/messages/clear"
        self.login()

        #act
        response = self.getResponse(path)
        
        # assert
        self.assertEquals(200, response.status_code)
    
    
    def testMessageCreateUrl(self):
        #arrange
        path = "/talk/messages/create"
        template = "geocamTalk/message_form.html"

        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)
    
    def testMessageJSONFeedUrl(self):
        #arrange
        path = "/talk/messages.json"
        
        #act
        guestResponse = self.getResponse(path)
        self.login();
        memberResponse = self.getResponse(path)
        
        #assert
        self.assertEqual(403, guestResponse.status_code, "should redirect if not logged in")
        self.assertEqual(200, memberResponse.status_code, "should display if logged in")

    def testMyMessageJSONFeedUrl(self):
        #arrange
        me = User.objects.all()[0]
        path = "/talk/messages/%s.json" % me.username   
        
        #act
        guestResponse = self.getResponse(path)
        self.login();
        memberResponse = self.getResponse(path)
        
        #assert
        self.assertEqual(403, guestResponse.status_code, "should redirect if not logged in")
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
        
    def testMessageListFilteredByUserUrl(self):
        author = User.objects.all()[1]
        recipient = User.objects.all()[2]
        
        #arrange
        # url design is /talk/messages/<recipient username>/<author username>
        path = "/talk/messages/%s/%s" % (recipient.username, author.username)
        template = "geocamTalk/message_list.html"
        
        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)
        
    def getResponse(self, path):
        return self.client.get(path)
    def login(self):
        return self.client.login(username = "rhornsby", password = "geocam")