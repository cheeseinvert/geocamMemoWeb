# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from geocamMemo.models import MemoMessage, get_user_string, get_latest_message_revisions

class GeocamMemoUnitTest(TestCase):
    fixtures = ['demoMemoMessages.json']
    
    def setUp(self):
        self.now = datetime.now()
    
    def testEnsureMessageTitleFormatIsCorrect(self):
        # arrange
        message = MemoMessage.objects.create(
            content="012345678901234567890123456789", content_timestamp=d, author_id=1)
        
        # act
        title = message.title()
        
        # assert
        self.assertEquals(19, len(title))
        self.assertEquals(message.content[:16] + "...", title)
        
    def testEnsureDateStringFormat(self):
        #arrange
        d = datetime.now()
        message = MemoMessage.objects.create(content="test", content_timestamp=d, author_id=1)
        #act
        datestring = message.get_date_string()
        #assert
        self.assertEqual(datestring, d.strftime("%m/%d %H:%M:%S"))
        
    def testEnsureAuthorStringFormat(self):
        #arrange
        userwithoutrealname = User.objects.create(username="userwithoutrealname", password="geocam")
        userwithfirstname = User.objects.create(username="userwithfirstname", password="geocam", first_name="First")
        userwithlastname = User.objects.create(username="userwithlastname", password="geocam", last_name="Last")
        userwithfullname = User.objects.create(username="userwithfullname", password="geocam", first_name="First", last_name="Last")
        
        messagewithoutrealname = MemoMessage.objects.create(content="userwithoutrealname", 
                                                              author=userwithoutrealname,
                                                              content_timestamp=self.now)
        messagewithfirstname = MemoMessage.objects.create(content="userwithfirstname", 
                                                            author=userwithfirstname,
                                                            content_timestamp=self.now)
        messagewithlastname = MemoMessage.objects.create(content="userwithlastname", 
                                                           author=userwithlastname,
                                                           content_timestamp=self.now)
        messagewithfullname = MemoMessage.objects.create(content="userwithfullname", 
                                                           author=userwithfullname,
                                                           content_timestamp=self.now)
        
        #act
        #assert
        self.assertEqual("userwithoutrealname", messagewithoutrealname.get_author_string())        
        self.assertEqual("userwithfirstname", messagewithfirstname.get_author_string())        
        self.assertEqual("userwithlastname", messagewithlastname.get_author_string())        
        self.assertEqual("First Last", messagewithfullname.get_author_string()) 
        
    def testEnsureHasGeoLocation(self):
        #arange
        nogeomessage = MemoMessage.objects.create(content="no geolocation here!", 
                                                    author_id=1,
                                                    content_timestamp=self.now) 
        geomessage =   MemoMessage.objects.create(content="geolocation here!", 
                                                    author_id=1, 
                                                    latitude=0.0, 
                                                    longitude=1.0,
                                                    content_timestamp=self.now) #one value is zero as 0 = false
        
        #act
        #assert
        assert(not nogeomessage.has_geolocation())
        assert(geomessage.has_geolocation())

