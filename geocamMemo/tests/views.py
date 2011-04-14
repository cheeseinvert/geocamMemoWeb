# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from geocamMemo.models import MemoMessage, get_user_string
import json
import time
from django.core.urlresolvers import reverse

class GeocamMemoMessageSaveTest(TestCase):
    fixtures = ['demoUsers.json', 'demoMemoMessages.json']

    cmusv_lat = 37.41029
    cmusv_lon = -122.05944
        
    def setUp(self):
        self.now = datetime.now()
        pass
    
    def tearDown(self):
        pass

    def test_createMessage(self):
        """ Create Geocam Message """
        
        msgCnt = MemoMessage.latest.all().count()
        
        content = "This is a message"
        author = User.objects.get(username="rhornsby")
        
        MemoMessage.objects.create(content=content,
                                    latitude=GeocamMemoMessageSaveTest.cmusv_lat,
                                    longitude=GeocamMemoMessageSaveTest.cmusv_lon,
                                    author=author,
                                    content_timestamp=self.now)
        newMsgCnt = MemoMessage.objects.all().count() 
        self.assertEqual(msgCnt + 1, newMsgCnt, "Creating a Message Failed.")
  
    def test_deleteMessage(self):
        """ Delete Geocam Message """
        
        msgCnt = MemoMessage.latest.all().count()
        msg = MemoMessage.latest.all()[1]
        # delete the first message and all it's revisions:
        msg.delete()
        newMsgCnt = MemoMessage.latest.all().count() 
        self.assertEqual(newMsgCnt + 1, msgCnt, "Deleting a Message Failed.")
              
    def test_submitFormToCreateMessage(self):
        
        content = "Whoa man, that burning building almost collapsed on me!"
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        
        response = self.client.post(reverse("memo_create_message"),
                                  data={"content":content,
                                        "latitude":GeocamMemoMessageSaveTest.cmusv_lat,
                                        "longitude":GeocamMemoMessageSaveTest.cmusv_lon})
        self.assertEqual(response.status_code, 200, "submitFormToCreateMessage Failed")

    def test_submitFormToCreateMessageJSON(self):
        msgCnt = MemoMessage.latest.all().count()
        content = "Whoa man, that burning building almost collapsed on me!"
        timestamp = self.now
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')        
        response = self.client.post(reverse("memo_create_message_json"),
                                  data={"message":json.dumps({
                                        "content": content,
                                        "contentTimestamp":time.mktime(timestamp.timetuple()),                                    
                                        "latitude":GeocamMemoMessageSaveTest.cmusv_lat,
                                        "longitude":GeocamMemoMessageSaveTest.cmusv_lon})})
        newMsgCnt = MemoMessage.latest.all().count() 
        self.assertEqual(response.status_code, 200, "submitFormToCreateMessageJSON Failed")
        self.assertEqual(newMsgCnt, msgCnt+1)
        
    def test_MessagesJsonFeed(self):
        ordered_messages = MemoMessage.getMessages()
        # yes the order of this dict does matter... unfortunately
        stringified_msg_list = json.dumps([msg.getJson() for msg in ordered_messages ])

        self.client.login(username="rhornsby", password='geocam')

        response = self.client.get(reverse("memo_message_list_all_json"))
        
        self.assertContains(response,stringified_msg_list)
        
    def test_MessageJsonFeed(self):
        # arrange
        msg = MemoMessage.latest.all().reverse()[0]
        stringified_msg = json.dumps(msg.getJson())
        
        #self.client.login(username="root", password='geocam')
        
        # act
        response = self.client.get(reverse("memo_message_details_json", args=[msg.pk]))
        
        # assert
        self.assertContains(response,stringified_msg)             
        
    def test_index(self):
        """ Test that we are forced to login to view webroot """
        
        response = self.client.get(reverse("memo_message_list_all"))
        # expect redirect to the login page:
        self.assertEqual(response.status_code, 302, "We didnt have to login to see the index page")
        self.assertTrue(self.client.login(username='jmiller',
                                        password='geocam'))
        response = self.client.get(reverse("memo_message_list_all"))
        # expect success because we are logged in:
        self.assertEqual(response.status_code, 200, "Logged in user cant see index page")   
        
    def test_login(self):
        """ Make sure all users can login """
        
        for u in User.objects.all():
            self.assertTrue(self.client.login(username=u.username, password='geocam'))

class GeocamMemoMessageEditAndDeleteTest(TestCase):
    fixtures = ['demoUsers.json', 'demoMemoMessages.json']
    
    def loginUser(self, author_pk):
        user = User.objects.get(pk=author_pk)
        self.client.login(username=user.username, password='geocam')

    def test_ensureEditByNonAuthorForbidden(self):
        original_msg = MemoMessage.getMessages()[0]
        
        for user in User.objects.all():
            if user.username != original_msg.author.username and not user.is_superuser:
                self.loginUser(user.pk)
                break                    
        modified_content = "The content has been modified"
        response = self.client.post(reverse("memo_edit_message", args=[original_msg.pk]),
                                  data={"content":modified_content,
                                        "author":original_msg.author.pk})
        self.assertEqual(response.status_code, 302, "ensureEditByNonAuthorForbidden Failed") 
        
        new_msg = MemoMessage.getMessages()[0]

        # should be redirected when form post is successful:
        self.assertEquals(new_msg.content, original_msg.content, "ensureEditByNonAuthorForbidden Failed")
        self.assertNotEqual(modified_content, new_msg.content, "ensureEditByNonAuthorForbidden Failed")
        self.assertEqual(new_msg.content_timestamp, original_msg.content_timestamp, "ensureEditByNonAuthorForbidden Failed")  
        self.assertEqual(new_msg.latitude, original_msg.latitude, "ensureEditByNonAuthorForbidden Failed")                                            
        self.assertEqual(new_msg.longitude, original_msg.longitude, "ensureEditByNonAuthorForbidden Failed")   
    
    def test_submitFormToEditMessage(self):        
        """ submit the Memo Message through the form """
        original_msg = MemoMessage.getMessages()[0]
        original_content = original_msg.content    
        self.loginUser(original_msg.author.pk)
        modified_content = "The content has been modified"
        response = self.client.post("/memo/messages/edit/%s"% original_msg.pk,
                                  data={"content":modified_content,
                                        "author":original_msg.author.pk})
        self.assertEqual(response.status_code, 302, "submitFormToEditMessage Failed") 
        
        new_msg = MemoMessage.getMessages()[0]
        self.assertNotEquals(new_msg.content, original_content, "submitFormToEditMessage Failed")
        self.assertEqual(modified_content, new_msg.content, "submitFormToEditMessage Failed")
        self.assertEqual(new_msg.content_timestamp, original_msg.content_timestamp, "submitFormToEditMessage Failed")  
        self.assertEqual(new_msg.latitude, original_msg.latitude, "submitFormToEditMessage Failed")                                            
        self.assertEqual(new_msg.longitude, original_msg.longitude, "submitFormToEditMessage Failed")                                            
                                          

    def test_ensureDeleteByNonAuthorForbidden(self):
        m = MemoMessage.latest.all()[0]
        msgCnt = MemoMessage.latest.all().count()
        
        for user in User.objects.all():
            if user.pk != m.author.pk and not user.is_superuser:
                self.loginUser(user.pk)
                break                    
        response = self.client.post("/memo/messages/delete/%s"% m.pk)                            
        self.assertEqual(response.status_code, 302, "ensureDeleteByNonAuthorForbidden Failed") 
        newMsgCnt = MemoMessage.latest.all().count()
        self.assertEqual(msgCnt, newMsgCnt, "ensureDeleteByNonAuthorForbidden Failed")

    def test_deleteMessage(self):
        "Delete the Memo Message"
        m = MemoMessage.latest.all()[0]
        msgCnt = MemoMessage.latest.all().count()
        self.loginUser(m.author.pk)
        response = self.client.post("/memo/messages/delete/%s"% m.pk)                                
        self.assertEqual(response.status_code, 302, "deleteMessage Failed")
        newMsgCnt = MemoMessage.latest.all().count()
        self.assertEqual(msgCnt - 1, newMsgCnt, "deleteMessage Failed")
        