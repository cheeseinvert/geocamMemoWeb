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

class GeocamTalkMessageSaveTest(TestCase):
    """
    Tests for GeocamTalk saving messages
    """   
    fixtures = ['teamUsers.json', 'msgs.json']

    cmusv_lat = 37.41029
    cmusv_lon = -122.05944
    
    def setUp(self):
        self.now = datetime.now()
        pass
    
    def tearDown(self):
        pass
       
    def test_createTalkMessage(self):
        """ Create Geocam Talk Message """
        
        msgCnt = len(get_latest_message_revisions(TalkMessage))
        
        content = "This is a message"
        author = User.objects.get(username="avagadia")
        
        TalkMessage.objects.create(content=content,
                                    latitude=GeocamTalkMessageSaveTest.cmusv_lat,
                                    longitude=GeocamTalkMessageSaveTest.cmusv_lon,
                                    author=author,
                                    content_timestamp=self.now)
        newMsgCnt = len(get_latest_message_revisions(TalkMessage)) 
        self.assertEqual(msgCnt + 1, newMsgCnt, "Creating a Talk Message Failed.")
  
    def test_deleteTalkMessage(self):
        """ Delete Geocam Talk Message """
        
        msgCnt = len(get_latest_message_revisions(TalkMessage))
        # delete the first message:
        msg = get_latest_message_revisions(TalkMessage)[1]
        numRevs = msg.get_revisions().count()
        msg.delete()
        newMsgCnt = len(get_latest_message_revisions(TalkMessage)) 
        self.assertEqual(newMsgCnt + numRevs, msgCnt, "Deleting a Talk Message Failed.")
              
    def test_submitFormToCreateMessage(self):
        """ submit the Talk Message through the form """
        
        msgCnt = len(get_latest_message_revisions(TalkMessage))
        content = "Whoa man, that burning building almost collapsed on me!"
        author = User.objects.get(username="avagadia")
        self.client.login(username=author.username, password='geocam')
        
        response = self.client.post("/talk/messages/create/",
                                  data={"content":content,
                                        "latitude":GeocamTalkMessageSaveTest.cmusv_lat,
                                        "longitude":GeocamTalkMessageSaveTest.cmusv_lon,
                                        "author":author.pk})
        # should be redirected when form post is successful:
        self.assertEqual(response.status_code, 302, "submitFormToCreateMessage Failed")
        newMsgCnt = len(get_latest_message_revisions(TalkMessage))
        self.assertEqual(msgCnt + 1, newMsgCnt, "Creating a Talk Message through view Failed.")
        
        
    def test_submitFormWithoutContentTalkMessage(self):
        """ submit the Talk Message without content through the form """
        
        msgCnt = len(get_latest_message_revisions(TalkMessage))
        author = User.objects.get(username="avagadia")
        self.client.login(username=author.username, password='geocam')
        
        response = self.client.post("/talk/messages/create/",
                                  data={"latitude":GeocamTalkMessageSaveTest.cmusv_lat,
                                        "longitude":GeocamTalkMessageSaveTest.cmusv_lon,
                                        "author":author.pk})
        # should get 200 on render_to_response when is_valid fails (which should occur)
        self.assertEqual(response.status_code, 200, "test_submitFormWithoutContentTalkMessage Failed")
        newMsgCnt = len(get_latest_message_revisions(TalkMessage))
        self.assertEqual(msgCnt, newMsgCnt, "Creating a Talk Message through view Succeeded with no content.")
         
               
    def test_login(self):
        """ Make sure all users can login """
        
        for u in User.objects.all():
            self.assertTrue(self.client.login(username=u.username, password='geocam'))
           
    def test_MessageContentOrdering(self):
        
        ordered_messages = get_latest_message_revisions(TalkMessage)
        response = self._get_messages_response()
        response_ordered_messages = response.context["gc_msg"]
        self.assertEqual(ordered_messages[0], response_ordered_messages[0], 'Ordering of the message in the message list is not right')
    
    def test_MessageJsonFeed(self):
        author = User.objects.get(username="avagadia")
        self.client.login(username=author.username, password='geocam')
        ordered_messages = TalkMessage.objects.all().order_by('content_timestamp').reverse()
        stringified_msg_list = [{'pk':msg.pk,
                                 'author':msg.get_author_string(), 
                                 'content':msg.content, 
                                 'content_timestamp':msg.get_date_string(),
                                 'has_geolocation':bool(msg.has_geolocation())} for msg in ordered_messages ]
        jsonSerializedString = json.dumps(stringified_msg_list)
        response = self.client.get('/talk/messagefeed.json')
        self.assertContains(response, jsonSerializedString)

    def _get_messages_response(self):
        
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self.client.get('/talk/messages/')
        return response
    