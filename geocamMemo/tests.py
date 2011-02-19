# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from models import GeocamMessage

class geocamMemoTest(TestCase):
    """
    Tests for geocamMemoWeb
    """

    fixtures = ['User.json', 'geocamMemo.json']

    
    def test_geocamMemo(self):
        pass
    
    def testListmessages(self):
        
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self.client.get('/messages/index')
        self.assertEqual(response.status_code, 200, "ensure all users can see list")
              
    def testMessageDateFormat(self):
        
        messages = GeocamMessage.objects.all()
        body = self._get_messages_body()
        for m in messages:
            self.assertContains(body, m.create_date.strftime("%m/%d %H:%M:%S"), None, 200)
        
    def testMessageAuthorFormat(self):
        
        messages = GeocamMessage.objects.all()
        body = self._get_messages_body()
        
        for m in messages:
            if m.author.first_name:
              self.assertContains(body, m.author.first_name + " " + m.author.last_name)
            else:
              self.assertContains(body, m.author.username)
        
    def testMessageContentFormat(self):
        
        messages = GeocamMessage.objects.all()
        body = self._get_messages_body()
        for m in messages:
            self.assertContains(body, m.content)
    
    def testMessageGeoLocationPresent(self):
        
        messages = GeocamMessage.objects.all()
        body = self._get_messages_body()
        geocount = 0
        for m in messages:
            if m.lat and m.lon:
              geocount = geocount+1
        
        self.assertContains(body, "GEO!", geocount)          
    
    def _get_messages_body(self):
        
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self.client.get('/messages/index')
        return response