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

    fixtures = ['messagelist_User.json', 'messagelist_GeocamMessage.json']

    
    def test_geocamMemo(self):
        pass
    
    def testMessageListSizeAndOrder(self):
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self._get_messages_response()
        
        displayedmessages = response.context[-1]['gc_msg'] # get the data object sent to the template
        displayed_message_ids = []
        for m in displayedmessages:
            displayed_message_ids.append(m.pk)
        
        messages = GeocamMessage.objects.order_by("create_date")
        message_ids = []        
        for m in messages:
            message_ids.append(m.pk)

        self.assertEqual(displayed_message_ids, message_ids, "Order should be the same")
              
    def testMessageListDateFormat(self):
        
        messages = GeocamMessage.objects.all()
        response = self._get_messages_response()
        for m in messages:
            self.assertContains(response, m.create_date.strftime("%m/%d %H:%M:%S"), None, 200)
        
    def testMessageListAuthorFormat(self):
        
        messages = GeocamMessage.objects.all()
        response = self._get_messages_response()
        
        for m in messages:
            if m.author.first_name:
              self.assertContains(response, m.author.first_name + " " + m.author.last_name)
            else:
              self.assertContains(response, m.author.username)
        
    def testMessageListContentFormat(self):
        
        messages = GeocamMessage.objects.all()
        response = self._get_messages_response()
        for m in messages:
            self.assertContains(response, m.content)
    
    def testMessageListGeoLocationPresent(self):
        
        messages = GeocamMessage.objects.all()
        response = self._get_messages_response()
        geocount = 0
        for m in messages:
            if m.lat and m.lon:
              geocount = geocount+1
        
        self.assertContains(response, "geoloc.png", geocount)          
    
    def _get_messages_response(self):
        
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self.client.get('/messages/index')
        return response