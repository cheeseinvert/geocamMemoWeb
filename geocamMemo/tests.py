# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from models import GeocamMessage


class geocamMemoTest(TestCase):
    """
    Tests for geocamMemoWeb
    """
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_geocamMemo(self):
        pass
    
    def test_createMessage(self):
        content = "This is a message"
        lat = 1245.4
        lon = 321.4
        author = User.objects.create(username="avagadia")
        create_date = datetime.now()
        
        msg = GeocamMessage.objects.create(content=content,
                                           lat=lat,
                                           lon=lon,
                                           author=author,
                                           create_date=create_date                                           
                                           )
        
    def test_submitFormToCreateMessage(self):
        content = "This is a message"
        lat = 1245.4
        lon = 321.4
        author = User.objects.create(username="avagadia")
        create_date = datetime.now()
        
        response = self.client.post("/memo/message/create/",
                                  data={"content":content,
                                        "lat":lat,
                                        "lon":lon,
                                        "author":author})
        self.assertEqual(response.status_code, 200, "submitFormToCreateMessage Failed")
        
