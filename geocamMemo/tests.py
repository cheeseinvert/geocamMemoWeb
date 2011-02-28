# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from models import GeocamMessage, get_user_string

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
        response = self.get_messages_response()
        
        displayedmessages = response.context['gc_msg'] # get the data object sent to the template
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
        response = self.get_messages_response()
        for m in messages:
            self.assertContains(response, m.content_timestamp.strftime("%m/%d %H:%M:%S"), None, 200)
        
    def testMessageListAuthorFormat(self):
        messages = GeocamMessage.objects.all()
        response = self.get_messages_response()
        
        for m in messages:
            if m.author.first_name:
              self.assertContains(response, m.author.first_name + " " + m.author.last_name)
            else:
              self.assertContains(response, m.author.username)
        
    def testMessageListContentFormat(self):
        
        messages = GeocamMessage.objects.all()
        response = self.get_messages_response()
        for m in messages:
            self.assertContains(response, m.content)
    
    def testMessageListGeoLocationPresent(self):
        # arrange
        messages = GeocamMessage.objects.all()
        response = self.get_messages_response()

        # act
        geocount = 0
        for m in messages:
            if m.latitude and m.longitude:
              geocount = geocount+1
        
        # assert
        self.assertContains(response, "geoloc.png", geocount)
        self.assertContains(response, 'data-rel="dialog"', geocount)
        
    def testEnsureMessagesAreFilteredByUser(self):
        # arrange
        user = User.objects.all()[1]
        messages = GeocamMessage.objects.filter(author = user.pk)
        
        notUserMessages = GeocamMessage.objects.exclude(author = user.pk)
        
        # act
        response = self.get_messages_response_filtered(user)
        
        # assert
        self.assertEqual(200, response.status_code)
        for m in messages:
            self.assertContains(response, m.content)
        for m in notUserMessages:
            self.assertNotContains(response, m.content)                
      
    def testEnsureFilteredMessageListSizeAndOrder(self):        
        #arrange
        u = User.objects.all()[1]     
        
        #descending (newest at top)
        messages = GeocamMessage.objects.filter(author = u.pk).order_by("-content_timestamp") 
        message_ids = []        
        for m in messages:
            message_ids.append(m.pk)   
        
        #act
        response = self.get_messages_response_filtered(u)
        
        #Looks at last parameter of context. Denoted by -1
        displayedmessages = response.context[-1]['gc_msg'] # get the data object sent to the template
        displayed_message_ids = []
        for m in displayedmessages:
            displayed_message_ids.append(m.pk)
        
        #assert
        self.assertEqual(displayed_message_ids, message_ids, "Order should be the same")
 
    def testEnsureMessageListAuthorLinksPresent(self):
        #arrange        
        messages = GeocamMessage.objects.all()
        
        #act
        response = self.get_messages_response()
        
        #assert
        for m in messages:            
            self.assertContains(response, 'href="/memo/messages/' + m.author.username)
    
    def testEnsureListAuthorPresent(self):
        #arrange
        u = User.objects.all()[1]
        
        #act
        response = self.get_messages_response_filtered(u)
        
        #assert            
        self.assertContains(response, 'Memos by ' + get_user_string(u))
    
    def testEnsureGetUserStringReturnsFullNameWhenFullNameExist(self):
        #arrange
        u = User(username="johndoe", password="geocam", first_name="John", last_name="Doe")
                        
        #assert
        self.assertEqual('John Doe', get_user_string(u))
          
    def testEnsureGetUserStringReturnsUserNameWhenFullNameDoesntExist(self):
        #arrange
        u = User(username="johndoe", password="geocam")                        
        #assert
        self.assertEqual('johndoe', get_user_string(u))

    def testEnsureMapDisplaysAndIsAtMostRecentMessageLocation(self):
        #arrange
        message = GeocamMessage.objects.all().order_by("-content_timestamp")[0]
        lat = message.latitude
        lon = message.longitude

        #act
        response = self.get_messages_response()
        
        #assert
        self.assertContains(response, "createMap("+str(lat)+","+str(lon)+")")
        self.assertContains(response, "<section id=\"map_canvas\"")
    
    def testEnsureMapDisplaysAllMessagesWithGeolocationByAllUsers(self):
        #arrange
        messages = GeocamMessage.objects.all().order_by("-content_timestamp")
                                
        #act
        response = self.get_messages_response()
        
        #assert
        for m in messages:
            if m.has_geolocation():
                self.assertContains(response, "google.maps.LatLng("+str(m.latitude)+","+str(m.longitude)+")")
                self.assertContains(response, "title: '"+m.content+"'")   
            else:
                self.assertNotContains(response, "google.maps.LatLng("+str(m.latitude)+","+str(m.longitude)+")")

    def testEnsureMapCentersOnLatestMessageWithGeolocation(self):
        # arrange
        GeocamMessage.objects.create(content="testing" , author = User.objects.all()[0]) # newest timestamp
        messages = GeocamMessage.objects.all().order_by("-content_timestamp")

        # act
        response = self.get_messages_response()

        # assert
        self.assertNotContains(response, "createMap(None")

    def testEnsureGeolocationDetectionExists(self):
        response = self.get_messages_response()
        self.assertContains(response, "navigator.geolocation.getCurrentPosition(success, failure)")  
        self.assertContains(response, "createMap(latitude, longitude)")

    def testEnsureGeolocationDetectionIsNotUsedOnFilteredList(self):
        #arrange
        u = User.objects.all()[1]
        response = self.get_messages_response_filtered(u)
        self.assertNotContains(response, "navigator.geolocation.getCurrentPosition(success, failure)")  
        
    def get_messages_response_filtered(self, user):
        self.client.login(username=user.username, password='geocam')
        response = self.client.get('/memo/messages/' + user.username)
        return response
    
    def get_messages_response(self):
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self.client.get('/memo/messages/')
        return response

class GeocamMemoMessageEditAndDeleteTest(TestCase):
    fixtures = ['teamUsers.json', 'msgs.json']
    
    def loginUser(self, author_pk):
        user = User.objects.get(pk=author_pk)
        self.client.login(username=user.username, password='geocam')

    def test_ensureEditByNonAuthorForbidden(self):
        original_msg = GeocamMessage.objects.all()[0]
        
        for user in User.objects.all():
            if user.pk != original_msg.author.pk and not user.is_superuser:
                self.loginUser(user.pk)
                break                    
        modified_content = "The content has been modified"
        response = self.client.post("/memo/messages/edit/%s"% original_msg.pk,
                                  data={"content":modified_content,
                                        "author":original_msg.author.pk})
        self.assertEqual(response.status_code, 302, "ensureEditByNonAuthorForbidden Failed") 
        
        new_msg = GeocamMessage.objects.get(pk=original_msg.pk)
        
        # should be redirected when form post is successful:
        self.assertEquals(new_msg.content, original_msg.content, "ensureEditByNonAuthorForbidden Failed")
        self.assertNotEqual(modified_content, new_msg.content, "ensureEditByNonAuthorForbidden Failed")
        self.assertEqual(new_msg.content_timestamp, original_msg.content_timestamp, "ensureEditByNonAuthorForbidden Failed")  
        self.assertEqual(new_msg.latitude, original_msg.latitude, "ensureEditByNonAuthorForbidden Failed")                                            
        self.assertEqual(new_msg.longitude, original_msg.longitude, "ensureEditByNonAuthorForbidden Failed")   
    
    def test_submitFormToEditMessage(self):        
        """ submit the Memo Message through the form """
        original_msg = GeocamMessage.objects.all()[0]        
        self.loginUser(original_msg.author.pk)
        modified_content = "The content has been modified"
        response = self.client.post("/memo/messages/edit/%s"% original_msg.pk,
                                  data={"content":modified_content,
                                        "author":original_msg.author.pk})
        self.assertEqual(response.status_code, 302, "submitFormToEditMessage Failed") 

        new_msg = GeocamMessage.objects.get(pk=original_msg.pk)
               
        self.assertNotEquals(new_msg.content, original_msg.content, "submitFormToEditMessage Failed")
        self.assertEqual(modified_content, new_msg.content, "submitFormToEditMessage Failed")
        self.assertEqual(new_msg.content_timestamp, original_msg.content_timestamp, "submitFormToEditMessage Failed")  
        self.assertEqual(new_msg.latitude, original_msg.latitude, "submitFormToEditMessage Failed")                                            
        self.assertEqual(new_msg.longitude, original_msg.longitude, "submitFormToEditMessage Failed")                                            
                                          

    def test_ensureDeleteByNonAuthorForbidden(self):
        m = GeocamMessage.objects.all()[0]
        msgCnt = GeocamMessage.objects.all().count()
        
        for user in User.objects.all():
            if user.pk != m.author.pk and not user.is_superuser:
                self.loginUser(user.pk)
                break                    
        response = self.client.post("/memo/messages/delete/%s"% m.pk)                            
        self.assertEqual(response.status_code, 302, "ensureDeleteByNonAuthorForbidden Failed") 
        newMsgCnt = GeocamMessage.objects.all().count()
        self.assertEqual(msgCnt, newMsgCnt, "ensureDeleteByNonAuthorForbidden Failed")

    def test_deleteMessage(self):
        "Delete the Memo Message"
        m = GeocamMessage.objects.all()[0]
        msgCnt = GeocamMessage.objects.all().count()
        self.loginUser(m.author.pk)
        response = self.client.post("/memo/messages/delete/%s"% m.pk)                                
        self.assertEqual(response.status_code, 302, "deleteMessage Failed")
        newMsgCnt = GeocamMessage.objects.all().count()
        self.assertEqual(msgCnt - 1, newMsgCnt, "deleteMessage Failed")

class GeocamMemoUnitTest(TestCase):
    fixtures = ['geocamMessage.json']
    def testEnsureMessageTitleFormatIsCorrect(self):
        # arrange
        message = GeocamMessage.objects.get(pk = 777)
        
        # act
        title = message.title()
        
        # assert
        self.assertEquals(19, len(title))
        self.assertEquals(message.content[:16] + "...", title)
        
    def testEnsureDateStringFormat(self):
        #arrange
        d = datetime.now()
        message = GeocamMessage.objects.create(content="test", content_timestamp=d, author_id=1)
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
        
        messagewithoutrealname = GeocamMessage.objects.create(content="userwithoutrealname", author=userwithoutrealname)
        messagewithfirstname = GeocamMessage.objects.create(content="userwithfirstname", author=userwithfirstname)
        messagewithlastname = GeocamMessage.objects.create(content="userwithlastname", author=userwithlastname)
        messagewithfullname = GeocamMessage.objects.create(content="userwithfullname", author=userwithfullname)
        
        #act
        #assert
        self.assertEqual("userwithoutrealname", messagewithoutrealname.get_author_string())        
        self.assertEqual("userwithfirstname", messagewithfirstname.get_author_string())        
        self.assertEqual("userwithlastname", messagewithlastname.get_author_string())        
        self.assertEqual("First Last", messagewithfullname.get_author_string()) 
        
    def testEnsureHasGeoLocation(self):
        #arange
        nogeomessage = GeocamMessage.objects.create(content="no geolocation here!", author_id=1) 
        geomessage =   GeocamMessage.objects.create(content="geolocation here!", author_id=1, 
                                                    latitude=0.0, longitude=1.0) #one value is zero as 0 = false
        
        #act
        #assert
        assert(not nogeomessage.has_geolocation())
        assert(geomessage.has_geolocation())

class GeocamMemoSingleMessageViewTest(TestCase):
    fixtures = ['messagelist_User.json', 'messagelist_GeocamMessage.json']

    def testEnsureProperFieldsAreDisplayed(self):
        # arrange
        m = GeocamMessage.objects.get(pk = 3)
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        
        # act
        response = self.client.get('/memo/messages/details/' + str(m.pk))
        
        # assert
        self.assertContains(response, str(m.latitude))
        self.assertContains(response, str(m.longitude))
        self.assertContains(response, str(m.altitude))
        self.assertContains(response, str(m.accuracy))

