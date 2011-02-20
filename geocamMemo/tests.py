# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from models import GeocamMessage


class GeocamMemoTest(TestCase):
    """
    Tests for geocamMemoWeb
    """
    fixtures = ['teamUsers.json', 'msgs.json']
    cmusv_lat = 37.41029
    cmusv_lon = -122.05944
        
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_geocamMemo(self):
        pass
    
    def test_createMessage(self):
        """ Create Geocam Message """
        
        msgCnt = GeocamMessage.objects.all().count()
        
        content = "This is a message"
        author = User.objects.get(username="avagadia")
        now = datetime.now()
        
        GeocamMessage.objects.create(content=content,
                                    latitude=GeocamMemoTest.cmusv_lat,
                                    longitude=GeocamMemoTest.cmusv_lon,
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
        
        response = self.client.post("/memo/message/create/",
                                  data={"content":content,
                                        "latitude":GeocamMemoTest.cmusv_lat,
                                        "longitude":GeocamMemoTest.cmusv_lon})
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
        self.assertEqual(response.status_code, 200, "Loged in user cant see index page")   
        
    def test_login(self):
        """ Make sure all users can login """
        
        for u in User.objects.all():
            self.assertTrue(self.client.login(username=u.username, password='geocam'))
