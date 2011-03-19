# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from geocamMemo.models import MemoMessage, get_user_string, get_latest_message_revisions
import json

class GeocamMemoMessageListJsonFeed(TestCase):
    fixtures = ['demoUsers.json', 'demoMemoMessages.json']
    
    def test_getMessageListJsonFeed(self):
        author = User.objects.get(username="rhornsby")
        self.client.login(username=author.username, password='geocam')
        ordered_messages = get_latest_message_revisions(MemoMessage);
        stringified_msg_list = [{'pk':msg.pk,
                                 'author':msg.get_author_string(), 
                                 'content':msg.content, 
                                 'content_timestamp':msg.get_date_string(),
                                 'latitude':msg.latitude,
                                 'longitude':msg.longitude,
                                 'accuracy':msg.accuracy
                                 } for msg in ordered_messages ]
        jsonSerializedString = json.dumps(stringified_msg_list)
        response = self.client.get('/memo/messages.json')
        self.assertContains(response, jsonSerializedString)

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
        
        msgCnt = MemoMessage.objects.all().count()
        
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
        
        msgCnt = MemoMessage.objects.all().count()
        msg = MemoMessage.objects.all()[1]
        numRevs = msg.get_revisions().count()
        # delete the first message and all it's revisions:
        msg.delete()
        newMsgCnt = MemoMessage.objects.all().count() 
        self.assertEqual(newMsgCnt + numRevs, msgCnt, "Deleting a Message Failed.")
              
    def test_submitFormToCreateMessage(self):
        
        content = "Whoa man, that burning building almost collapsed on me!"
        author = User.objects.get(username="rhornsby")
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
        self.assertTrue(self.client.login(username='jmiller',
                                        password='geocam'))
        response = self.client.get('/')
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

    #TODO: Resolve revisions issue where get_latest_revision() is throwing exception
#===============================================================================
#    def test_ensureEditByNonAuthorForbidden(self):
#        original_msg = get_latest_message_revisions(MemoMessage)[0]
#        
#        for user in User.objects.all():
#            if user.pk != original_msg.author.pk and not user.is_superuser:
#                self.loginUser(user.pk)
#                break                    
#        modified_content = "The content has been modified"
#        response = self.client.post("/memo/messages/edit/%s"% original_msg.pk,
#                                  data={"content":modified_content,
#                                        "author":original_msg.author.pk})
#        self.assertEqual(response.status_code, 302, "ensureEditByNonAuthorForbidden Failed") 
#        
#        new_msg = original_msg.get_latest_revision()
# 
#        
#        # should be redirected when form post is successful:
#        self.assertEquals(new_msg.content, original_msg.content, "ensureEditByNonAuthorForbidden Failed")
#        self.assertNotEqual(modified_content, new_msg.content, "ensureEditByNonAuthorForbidden Failed")
#        self.assertEqual(new_msg.content_timestamp, original_msg.content_timestamp, "ensureEditByNonAuthorForbidden Failed")  
#        self.assertEqual(new_msg.latitude, original_msg.latitude, "ensureEditByNonAuthorForbidden Failed")                                            
#        self.assertEqual(new_msg.longitude, original_msg.longitude, "ensureEditByNonAuthorForbidden Failed")   
#===============================================================================
    #===========================================================================
    # 
    # def test_submitFormToEditMessage(self):        
    #    """ submit the Memo Message through the form """
    #    original_msg = get_latest_message_revisions(MemoMessage)[0]
    #    original_content = original_msg.content    
    #    self.loginUser(original_msg.author.pk)
    #    modified_content = "The content has been modified"
    #    response = self.client.post("/memo/messages/edit/%s"% original_msg.pk,
    #                              data={"content":modified_content,
    #                                    "author":original_msg.author.pk})
    #    self.assertEqual(response.status_code, 302, "submitFormToEditMessage Failed") 
    #    
    #    new_msg = original_msg.get_latest_revision()
    #    self.assertNotEquals(new_msg.content, original_content, "submitFormToEditMessage Failed")
    #    self.assertEqual(modified_content, new_msg.content, "submitFormToEditMessage Failed")
    #    self.assertEqual(new_msg.content_timestamp, original_msg.content_timestamp, "submitFormToEditMessage Failed")  
    #    self.assertEqual(new_msg.latitude, original_msg.latitude, "submitFormToEditMessage Failed")                                            
    #    self.assertEqual(new_msg.longitude, original_msg.longitude, "submitFormToEditMessage Failed")                                            
    #===========================================================================
                                          

    def test_ensureDeleteByNonAuthorForbidden(self):
        m = MemoMessage.objects.all()[0]
        msgCnt = MemoMessage.objects.all().count()
        
        for user in User.objects.all():
            if user.pk != m.author.pk and not user.is_superuser:
                self.loginUser(user.pk)
                break                    
        response = self.client.post("/memo/messages/delete/%s"% m.pk)                            
        self.assertEqual(response.status_code, 302, "ensureDeleteByNonAuthorForbidden Failed") 
        newMsgCnt = MemoMessage.objects.all().count()
        self.assertEqual(msgCnt, newMsgCnt, "ensureDeleteByNonAuthorForbidden Failed")

    def test_deleteMessage(self):
        "Delete the Memo Message"
        m = get_latest_message_revisions(MemoMessage)[0]
        msgCnt = MemoMessage.objects.all().count()
        numRevs = m.get_revisions().count()
        self.loginUser(m.author.pk)
        response = self.client.post("/memo/messages/delete/%s"% m.pk)                                
        self.assertEqual(response.status_code, 302, "deleteMessage Failed")
        newMsgCnt = MemoMessage.objects.all().count()
        self.assertEqual(msgCnt - numRevs, newMsgCnt, "deleteMessage Failed")
        