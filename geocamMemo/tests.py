# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from models import GeocamMessage

class GeocamMemoMessageSaveTest(TestCase):
    fixtures = ['teamUsers.json', 'msgs.json']

    cmusv_lat = 37.41029
    cmusv_lon = -122.05944
        
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_createMessage(self):
        """ Create Geocam Message """
        
        msgCnt = GeocamMessage.objects.all().count()
        
        content = "This is a message"
        author = User.objects.get(username="avagadia")
        now = datetime.now()
        
        GeocamMessage.objects.create(content=content,
                                    latitude=GeocamMemoMessageSaveTest.cmusv_lat,
                                    longitude=GeocamMemoMessageSaveTest.cmusv_lon,
                                    author=author,
                                    content_timestamp=now)
        newMsgCnt = GeocamMessage.objects.all().count() 
        self.assertEqual(msgCnt + 1, newMsgCnt, "Creating a Message Failed.")
  
    def test_deleteMessage(self):
        """ Delete Geocam Message """
        
        msgCnt = GeocamMessage.objects.all().count()
        # delete the first message:
        GeocamMessage.objects.all()[1].delete()
        newMsgCnt = GeocamMessage.objects.all().count() 
        self.assertEqual(newMsgCnt + 1, msgCnt, "Deleting a Message Failed.")
              
    def test_submitFormToCreateMessage(self):
        
        content = "Whoa man, that burning building almost collapsed on me!"
        author = User.objects.get(username="avagadia")
        self.client.login(username=author.username, password='geocam')
        
        response = self.client.post("/memo/messages/create/",
                                  data={"content":content,
                                        "latitude":GeocamMemoMessageSaveTest.cmusv_lat,
                                        "longitude":GeocamMemoMessageSaveTest.cmusv_lon})
        self.assertEqual(response.status_code, 200, "submitFormToCreateMessage Failed")
        
    def test_index(self):
        """ Test that we are forced to login to view webroot """
        
        response = self.client.get('/')
        # expect redirect to the login page:
        self.assertEqual(response.status_code, 302, "We didnt have to login to see the index page")
        self.assertTrue(self.client.login(username='adamg',
                                        password='geocam'))
        response = self.client.get('/')
        # expect success because we are logged in:
        self.assertEqual(response.status_code, 200, "Logged in user cant see index page")   
        
    def test_login(self):
        """ Make sure all users can login """
        
        for u in User.objects.all():
            self.assertTrue(self.client.login(username=u.username, password='geocam'))

class GeocamMemoListViewTest(TestCase):
    fixtures = ['messagelist_User.json', 'messagelist_GeocamMessage.json']
    
    def testMessageListSizeAndOrder(self):
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self._get_messages_response()
        
        displayedmessages = response.context[-1]['gc_msg'] # get the data object sent to the template
        displayed_message_ids = []
        for m in displayedmessages:
            displayed_message_ids.append(m.pk)
        
        messages = GeocamMessage.objects.order_by("-content_timestamp") #descending (newest at top)
        message_ids = []        
        for m in messages:
            message_ids.append(m.pk)

        self.assertEqual(displayed_message_ids, message_ids, "Order should be the same")

              
    def testMessageListDateFormat(self):
        
        messages = GeocamMessage.objects.all()
        response = self._get_messages_response()
        for m in messages:
            self.assertContains(body, m.content_timestamp.strftime("%m/%d %H:%M:%S"), None, 200)
        
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
            if m.latitude and m.longitude:
              geocount = geocount+1
        
        self.assertContains(response, "geoloc.png", geocount)          
    
    def _get_messages_response(self):
        
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self.client.get('/memo/messages/')
        return response
