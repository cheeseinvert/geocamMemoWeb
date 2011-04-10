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
import array
import random
import os
from django.core.urlresolvers import reverse

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
        
        response = self.client.post(reverse("talk_create_message"),
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

        response = self.client.post(reverse("talk_create_message"),
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
    
    def test_submitFormToCreateMessageJSON(self):
        msgCnt = TalkMessage.latest.all().count()
        content = "Whoa man, that burning building almost collapsed on me!"
        timestamp = self.now
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')        
        response = self.client.post(reverse("talk_create_message_json"),
                                  data={"message":json.dumps({
                                        "content": content,
                                        "contentTimestamp":timestamp.strftime("%m/%d/%y %H:%M:%S"),                                    
                                        "latitude":GeocamTalkMessageSaveTest.cmusv_lat,
                                        "longitude":GeocamTalkMessageSaveTest.cmusv_lon})})
        newMsgCnt = TalkMessage.latest.all().count() 
        self.assertEqual(response.status_code, 200, "submitFormToCreateMessageJSON Failed")
        self.assertContains(response, "messageId")
        self.assertContains(response, "authorFullname")
        self.assertEqual(newMsgCnt, msgCnt+1)
        
    def testAudioMsgCreate(self):
        msgCnt = TalkMessage.latest.all().count()
        content = "Whoa man, that burning building almost collapsed on me!"
        timestamp = self.now
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')   
        audioFile = 'media/geocamTalk/test/test.mp4'
        self._createFile(filename=audioFile, filesize=100*1024)
        f = open(audioFile, "rb")
        response = self.client.post(reverse("talk_create_message_json"),
                                    data={'audio':f,
                                          "message":json.dumps({
                                        "content": content,
                                        "contentTimestamp":timestamp.strftime("%m/%d/%y %H:%M:%S"),                                    
                                        "latitude":GeocamTalkMessageSaveTest.cmusv_lat,
                                        "longitude":GeocamTalkMessageSaveTest.cmusv_lon})})
        f.close() 
        self._clean_test_files('test.mp4')
        self.assertEqual(response.status_code, 200, "Failed to move message from phone to web app")
    
    def _createFile(self, filename, filesize=5*1024*1024):
        """Create and fill a file with random data"""
        blocksize = 4096 # 4k
        datablock = array.array('I')
        written = 0
        # Create a datablock:
        while written < blocksize:
            datablock.append(random.getrandbits(32))
            written = written + 4
            
        with open(filename, 'w') as f:
            written = 0
            while written < filesize:
                datablock.tofile(f)
                written += blocksize
            f.flush()
            os.fsync(f.fileno())
    
    def _clean_test_files(self, filename):
        folder = 'media/geocamTalk/test'
        post_folder = 'media/geocamTalk/audio'
        post_file_path = os.path.join(post_folder, filename)
        os.unlink(post_file_path)
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                os.unlink(file_path)
            except Exception, e:
                print e
                
    def test_submitFormWithoutContentTalkMessage(self):
        """ submit the Talk Message without content through the form """
        
        msgCnt = TalkMessage.latest.all().count()
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        
        response = self.client.post(reverse("talk_create_message"),
                                  data={"latitude":GeocamTalkMessageSaveTest.cmusv_lat,
                                        "longitude":GeocamTalkMessageSaveTest.cmusv_lon,
                                        "author":author.pk})
        # should get 200 on render_to_response when is_valid fails (which should occur)
        self.assertEqual(response.status_code, 200, "test_submitFormWithoutContentTalkMessage Failed")
        newMsgCnt = TalkMessage.latest.all().count()
        self.assertEqual(msgCnt, newMsgCnt, "Creating a Talk Message through view Succeeded with no content.")
         
              
    def test_MessageJsonFeed(self):
        # arrange
        msg = TalkMessage.latest.all()[0]
        stringified_msg = json.dumps(msg.getJson())
        
        self.client.login(username=msg.author.username, password='geocam')
        
        # act
        response = self.client.get(reverse("talk_message_details_json", args=[msg.pk]))
        
        # assert
        self.assertContains(response,stringified_msg)                    
               
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
        # arrange
        ''' This test is attempting to verify that we see messages for specified user or broadcast '''
        recipient = User.objects.get(username="acurie")
        author = User.objects.all()[1]
        msg = TalkMessage.objects.create(content='yo dude', content_timestamp=self.now, author=author)
        msg.recipients.add(recipient)
        msg.recipients.add(User.objects.all()[2])
        
        time_stamp = TalkMessage.objects.all().order_by('-pk')[0].pk - 2
        profile = recipient.profile
        profile.last_viewed_mymessages = time_stamp
        profile.save()
 
        #self.client.login(username=recipient.username, password='geocam')
        #response = self.client.get('/talk/messages/'+recipient_path)
        
        # act
        response = self._get_messages_response(recipient=recipient)
        expectedMessages = TalkMessage.getMessages(recipient,author=None) # don't pass in author
        gotMessages = response.context["gc_msg"]
        
        # assert
        self.assertTrue(time_stamp < recipient.profile.last_viewed_mymessages)
        
        self.assertEqual(recipient, response.context["recipient"])
        self.assertEqual(len(gotMessages), expectedMessages.count(), "My messages response % is not the same size as expected %s" % (len(gotMessages), expectedMessages.count()))        

        for i in range(len(expectedMessages)):
            self.assertEqual(expectedMessages[i],gotMessages[i], "My messages doesn't contain an expected message: %s" % expectedMessages[i])
       
        
    @staticmethod
    def cmpMessageSortNewestFirst(message1, message2):
        if(message1.content_timestamp > message2.content_timestamp):
            return -1
        if(message1.content_timestamp == message2.content_timestamp):
            return 0
        else:
            return 1    
    
    def test_NewMessageCountJsonFeed(self):
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        # need to cast the query set to a list here to avoid the dynamic update 
        # when we create the new msg
        #old_messages = list(TalkMessage.getMessages())
        before_new_message = TalkMessage.getLargestMessageId()
        recipient = User.objects.get(username="acurie")
        msg = TalkMessage.objects.create(content='This is a new message', content_timestamp=datetime.now(), author=author)
        msg.recipients.add(recipient)
        msg.recipients.add(User.objects.all()[2])
        msg.save()
        response = self.client.get(reverse("talk_message_list_author_json", args=[author.username])+
                                   '?since=%s' % before_new_message)
        self.assertContains(response, '"msgCnt": 1')
        # I dont want to delete this because I wasted a bunch of time on it:
        #for oldmsg in old_messages:
        #    self.assertNotContains(response, '"messageId": %s' % oldmsg.pk)
        
    def test_MessageJsonFeed(self):
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        ordered_messages = TalkMessage.objects.all().order_by('-pk')
        messageid = ordered_messages[0].pk - 1
        response = self.client.get(reverse("talk_message_list_all_json")+'?since=%s' % messageid)
        self.assertContains(response, '"messageId": %s' % ordered_messages[0].pk)
        self.assertContains(response, '"authorUsername": "%s"' % ordered_messages[0].author.username)
        self.assertContains(response, '"authorFullname": "%s"' % ordered_messages[0].get_author_string())
        self.assertContains(response, '"userId": %s' % ordered_messages[0].author.pk)
        recipient_string = ", ".join('"%s"' % r.username for r in ordered_messages[0].recipients.all())
        self.assertContains(response, '"recipients": [%s]' % recipient_string)
        self.assertContains(response, '"content": "%s"' % ordered_messages[0].content)
        self.assertContains(response, '"contentTimestamp": "%s"' % ordered_messages[0].get_date_string())
        self.assertContains(response, '"hasGeolocation": %s' % str(ordered_messages[0].has_geolocation()).lower())
        self.assertContains(response, '"latitude": %s' % ordered_messages[0].latitude)
        self.assertContains(response, '"longitude": %s' % ordered_messages[0].longitude)
        self.assertContains(response, '"accuracy": %s' % ordered_messages[0].accuracy)
        for msg in ordered_messages[1:]:
            self.assertNotContains(response, '"messageId": %s' % msg.pk)
      
    def test_MyMessageJsonFeed(self):
        ''' This test is attempting to verify that we see messages for specified user or broadcast '''
            
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        ordered_messages = TalkMessage.getMessages(recipient=author).order_by("-pk")
        
        messageid = ordered_messages[0].pk - 1
        response = self.client.get(reverse("talk_message_list_author_json", args=[author.username])+
                                   '?since=%s' % messageid)
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
    