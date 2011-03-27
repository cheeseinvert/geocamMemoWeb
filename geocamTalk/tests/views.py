# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import time
from geocamTalk.models import TalkMessage
import json
import re

class GeocamTalkMessageSaveTest(TestCase):
    """
    Tests for GeocamTalk saving messages
    """   
    fixtures = ['demoUsers.json', 'demoTalkMessages.json']

    cmusv_lat = 37.41029
    cmusv_lon = -122.05944
    
    def setUp(self):
        self.now = datetime.now()
        pass
    
    def tearDown(self):
        pass
       
    def test_createTalkMessage(self):
        """ Create Geocam Talk Message """
        
        msgCnt = TalkMessage.latest.all().count()
        
        content = "This is a message"
        author = User.objects.get(username="rhornsby")
        
        TalkMessage.objects.create(content=content,
                                    latitude=GeocamTalkMessageSaveTest.cmusv_lat,
                                    longitude=GeocamTalkMessageSaveTest.cmusv_lon,
                                    author=author,
                                    content_timestamp=self.now)
        newMsgCnt = TalkMessage.latest.all().count()
        self.assertEqual(msgCnt + 1, newMsgCnt, "Creating a Talk Message Failed.")
  
    def test_deleteTalkMessage(self):
        """ Delete Geocam Talk Message """
        
        msgCnt = TalkMessage.latest.all().count()
        # delete the first message:
        msg = TalkMessage.latest.all()[1]
        msg.delete()
        newMsgCnt = TalkMessage.latest.all().count() 
        self.assertEqual(newMsgCnt + 1, msgCnt, "Deleting a Talk Message Failed.")
              
    def test_submitFormToCreateMessage(self):
        """ submit the Talk Message through the form """
        
        msgCnt = TalkMessage.latest.all().count()
        content = "Whoa man, that burning building almost collapsed on me!"
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        
        response = self.client.post("/talk/messages/create/",
                                  data={"content":content,
                                        "latitude":GeocamTalkMessageSaveTest.cmusv_lat,
                                        "longitude":GeocamTalkMessageSaveTest.cmusv_lon,
                                        "author":author.pk})
        # should be redirected when form post is successful:
        self.assertEqual(response.status_code, 302, "submitFormToCreateMessage Failed")
        newMsgCnt = TalkMessage.latest.all().count()
        self.assertEqual(msgCnt + 1, newMsgCnt, "Creating a Talk Message through view Failed.")
 
    def test_submitFormToCreateMessageWithRecipients(self):
        """ submit the Talk Message through the form """
        
        msgCnt = TalkMessage.latest.all().count()
        content = "Whoa man, that burning building almost collapsed on me!"
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        
        recipienta = User.objects.all()[1]
        recipientb = User.objects.all()[2]

        response = self.client.post("/talk/messages/create/",
                                  data={"content":content,
                                        "latitude":GeocamTalkMessageSaveTest.cmusv_lat,
                                        "longitude":GeocamTalkMessageSaveTest.cmusv_lon,
                                        "author":author.pk,
                                        "recipients":[recipienta.pk, recipientb.pk]})
        
        # should be redirected when form post is successful:
        self.assertEqual(response.status_code, 302, "submitFormToCreateMessage Failed")
        newMsgCnt = TalkMessage.latest.all().count()
        self.assertEqual(msgCnt + 1, newMsgCnt, "Creating a Talk Message through view Failed.") 
        newMsg = TalkMessage.getMessages()[0]
        self.assertEqual(newMsg.recipients.all().count(), 2, "Different number of recipients than expected")
        
    def test_submitFormWithoutContentTalkMessage(self):
        """ submit the Talk Message without content through the form """
        
        msgCnt = TalkMessage.latest.all().count()
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        
        response = self.client.post("/talk/messages/create/",
                                  data={"latitude":GeocamTalkMessageSaveTest.cmusv_lat,
                                        "longitude":GeocamTalkMessageSaveTest.cmusv_lon,
                                        "author":author.pk})
        # should get 200 on render_to_response when is_valid fails (which should occur)
        self.assertEqual(response.status_code, 200, "test_submitFormWithoutContentTalkMessage Failed")
        newMsgCnt = TalkMessage.latest.all().count()
        self.assertEqual(msgCnt, newMsgCnt, "Creating a Talk Message through view Succeeded with no content.")
         
               
    def test_login(self):
        """ Make sure all users can login """
        
        for u in User.objects.all():
            self.assertTrue(self.client.login(username=u.username, password='geocam'))
           
    def test_MessageContentOrdering(self):
        
        ordered_messages = TalkMessage.latest.all().order_by('-content_timestamp')
        response = self._get_messages_response()
        response_ordered_messages = response.context["gc_msg"]
        self.assertEqual(ordered_messages[0], response_ordered_messages[0], 'Ordering of the message in the message list is not right')
    
    def test_MyMessageList(self):
        ''' This test is attempting to verify that we see messages for specified user or broadcast '''
        recipient = User.objects.get(username="acurie")
        author = User.objects.all()[1]
        msg = TalkMessage.objects.create(content='yo dude', content_timestamp=self.now, author=author)
        msg.recipients.add(recipient)
        msg.recipients.add(User.objects.all()[2])
 
        response = self._get_messages_response(recipient=recipient)
        # dont pass in author here:
        expectedMessages = TalkMessage.getMessages(recipient,author=None)      
        
        gotMessages = response.context["gc_msg"]
        self.assertEqual(recipient, response.context["recipient"])
        self.assertEqual(len(gotMessages), expectedMessages.count(), "My messages response % is not the same size as expected %s" % (len(gotMessages), expectedMessages.count()))        

        for i in range(len(expectedMessages)):
            self.assertEqual(expectedMessages[i],gotMessages[i], "My messages doesn't contain an expected message: %s" % expectedMessages[i])
       
    def test_MessageListGetsServerTimestamp(self):
        ''' This test is attempting to verify that we get the server timestamp in the passed context '''
        timestamp = int(time.mktime(datetime.now().timetuple())) 
        response = self._get_messages_response()     
        try:
            gotTimestamp = response.context["timestamp"]
        except:
            self.fail("we didn't get the timestamp in the passed context to list_messages template")
        self.assertTrue(gotTimestamp >= timestamp, "The server timestamp was not accurate")
         
    @staticmethod
    def cmpMessageSortNewestFirst(message1, message2):
        if(message1.content_timestamp > message2.content_timestamp):
            return -1
        if(message1.content_timestamp == message2.content_timestamp):
            return 0
        else:
            return 1    
    
    def test_NewMessageJsonFeed(self):
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        # need to cast the query set to a list here to avoid the dynamic update 
        # when we create the new msg
        #old_messages = list(TalkMessage.getMessages())
        before_new_message = int(time.time() * 1000 * 1000)
        time.sleep(1)
        recipient = User.objects.get(username="acurie")
        msg = TalkMessage.objects.create(content='This is a new message', content_timestamp=datetime.now(), author=author)
        msg.recipients.add(recipient)
        msg.recipients.add(User.objects.all()[2])
        msg.save()
        response = self.client.get('/talk/messagefeed/?since=%s' % before_new_message)
        self.assertContains(response, '"msgCnt": 1')
        # I dont want to delete this because I wasted a bunch of time on it:
        #for oldmsg in old_messages:
        #    self.assertNotContains(response, '"messageId": %s' % oldmsg.pk)
        
    def test_MessageJsonFeed(self):
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        ordered_messages = TalkMessage.objects.all().order_by('content_timestamp').reverse()
        latest_msgs_dt = ordered_messages[0].content_timestamp - timedelta(seconds=5)
        ts = int(time.mktime(latest_msgs_dt.timetuple()) * 1000 * 1000)
        response = self.client.get('/talk/messagefeed/?since=%s' % ts)
        self.assertContains(response, '"messageId": %s' % ordered_messages[0].pk)
        for msg in ordered_messages[1:]:
            self.assertNotContains(response, '"messageId": %s' % msg.pk)
      
    def test_MyMessageJsonFeed(self):
        ''' This test is attempting to verify that we see messages for specified user or broadcast '''
            
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        ordered_messages = TalkMessage.getMessages(recipient=author)
        
        latest_msgs_dt = ordered_messages[0].content_timestamp - timedelta(seconds=5)
        ts = int(time.mktime(latest_msgs_dt.timetuple()) * 1000 * 1000)
        response = self.client.get('/talk/messagefeed/rhornsby?since=%s' % ts)
        self.assertContains(response, '"messageId": %s' % ordered_messages[0].pk)
        for msg in ordered_messages[1:]:
            self.assertNotContains(response, '"messageId": %s' % msg.pk)

    def _get_messages_response(self, recipient=None):
        recipient_path = ""
        if recipient is None:
            recipient = User.objects.all()[0]
        else:
            recipient_path = recipient.username
        self.client.login(username=recipient.username, password='geocam')
        response = self.client.get('/talk/messages/'+recipient_path)
        return response
    