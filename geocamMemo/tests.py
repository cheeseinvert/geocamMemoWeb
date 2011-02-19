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
        print "listmessages test!"
        
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self.client.get('/messages/index')
        self.assertEqual(response.status_code, 200, "ensure all users can see list")
        
        #        messages = GeocamMessage.objects.all()
        
