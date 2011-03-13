# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from geocamMemo.models import MemoMessage, get_user_string, get_latest_message_revisions

class GeocamMemoUrls(TestCase):
    fixtures = ['demoUsers.json', 'demoMemoMessages.json']
    
    def testMessageListUrl(self):
        #arrange
        path = "/memo/messages/"   
        template = "geocamMemo/messagelist.html"

        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)
        
    def testMessageDetailsUrl(self):
        #arrange
        message = get_latest_message_revisions(MemoMessage)[0]
        path = "/memo/messages/details/" + str(message.pk)
        template = "geocamMemo/details.html"

        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)

    def testMessageEditUrl(self):
        #arrange
        message = get_latest_message_revisions(MemoMessage)[0]
        path = "/memo/messages/edit/" + str(message.pk)
        template = "geocamMemo/edit_message_form.html"

        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)
    
    def testMessageCreateUrl(self):
        #arrange
        path = "/memo/messages/create"
        template = "geocamMemo/message_form.html"

        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)
    
    def testMessageListFilteredByUserUrl(self):
        #arrange
        path = "/memo/messages/root"
        template = "geocamMemo/messagelist.html"
        
        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template)
    
    def testMessageDeleteUrl(self):
        #arrange
        message = get_latest_message_revisions(MemoMessage)[0]
        path = "/memo/messages/delete/" + str(message.pk)

        #act
        guestResponse = self.getResponse(path)
        self.login();
        memberResponse = self.getResponse(path)
        
        #assert
        self.assertEqual(302, guestResponse.status_code, "should redirect if not logged in")
        self.assertEqual(302, memberResponse.status_code, "should redirect upon deletion")
        
    def testMapViewUrl(self):
       #arrange
        path = "/memo/map/"   
        template = "geocamMemo/map.html"

        #act
        self.assertPathRequiresLoginAndUsesTemplate(path, template) 

   

    
    
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
        return self.client.login(username = "root", password = "geocam")