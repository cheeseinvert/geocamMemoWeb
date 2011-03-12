# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from geocamMemo.models import MemoMessage, get_user_string, get_latest_message_revisions



class GeocamMemoListViewTest(TestCase):
    fixtures = ['messagelist_User.json', 'messagelist_GeocamMessage.json']
    
    def setUp(self):
        self.now = datetime.now()
        pass
    
    def tearDown(self):
        pass


    def testMessageListSizeAndOrder(self):
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self.get_messages_response()
        
        displayedmessages = response.context['gc_msg'] # get the data object sent to the template
        displayed_message_ids = []
        for m in displayedmessages:
            displayed_message_ids.append(m.pk)
        
        messages = get_latest_message_revisions(MemoMessage) #descending (newest at top)
        message_ids = []        
        for m in messages:
            message_ids.append(m.pk)

        self.assertEqual(displayed_message_ids, message_ids, "Order should be the same")

    def testMessageListDateFormat(self):
        messages = get_latest_message_revisions(MemoMessage)
        response = self.get_messages_response()
        for m in messages:
            self.assertContains(response, m.content_timestamp.strftime("%m/%d %H:%M:%S"), None, 200)
        
    def testMessageListAuthorFormat(self):
        messages = MemoMessage.objects.all()
        response = self.get_messages_response()
        
        for m in messages:
            if m.author.first_name:
              self.assertContains(response, m.author.first_name + " " + m.author.last_name)
            else:
              self.assertContains(response, m.author.username)
        
    def testMessageListContentFormat(self):
        
        messages = get_latest_message_revisions(MemoMessage)
        response = self.get_messages_response()
        for m in messages:
            self.assertContains(response, m.content)
    
    def testMessageListGeoLocationPresent(self):
        # arrange
        messages = get_latest_message_revisions(MemoMessage)
        response = self.get_messages_response()

        # act
        geocount = 0
        for m in messages:
            if m.latitude and m.longitude:
              geocount = geocount+1
        
        # assert
        self.assertContains(response, "data-icon=\"geoCam-map\"", geocount)
        self.assertContains(response, 'data-rel="dialog"', geocount)
        
    def testEnsureMessagesAreFilteredByUser(self):
        # arrange
        user = User.objects.all()[1]
        messages = MemoMessage.objects.filter(author = user.pk)
        
        notUserMessages = MemoMessage.objects.exclude(author = user.pk)
        
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
        messages = MemoMessage.objects.filter(author = u.pk).order_by("-content_timestamp") 
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
        messages = MemoMessage.objects.all()
        
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

class GeocamMemoMapViewTest(TestCase):
    fixtures = ['messagelist_User.json', 'messagelist_GeocamMessage.json']

    def testEnsureMapCentersOnLatestMessageWithGeolocation(self):
        # arrange
        MemoMessage.objects.create(content="testing", 
                                     author = User.objects.all()[0],
                                     content_timestamp=datetime.now()) # newest timestamp

        # act
        response = self.get_map_response()

        # assert
        self.assertNotContains(response, "createMap(None")

    def testEnsureMapDisplaysAllMessagesWithGeolocationByAllUsers(self):
        #arrange
        messages = get_latest_message_revisions(MemoMessage)
        message = messages[0]
        lat = message.latitude
        lon = message.longitude

        #act
        response = self.get_map_response()
        
        #assert
        self.assertContains(response, "createMap("+str(lat)+","+str(lon)+")")
        self.assertContains(response, "<section id=\"map_canvas\"")
        for m in messages:
            if m.has_geolocation():
                self.assertContains(response, "google.maps.LatLng("+str(m.latitude)+","+str(m.longitude)+")")
            else:
                self.assertNotContains(response, "google.maps.LatLng("+str(m.latitude)+","+str(m.longitude)+")")
                
    def get_map_response(self):
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self.client.get('/memo/map/')
        return response                

class GeocamMemoSingleMessageViewTest(TestCase):
    fixtures = ['messagelist_User.json', 'messagelist_GeocamMessage.json']

    def testEnsureProperFieldsAreDisplayed(self):
        # arrange
        m = get_latest_message_revisions(MemoMessage)[0]
        
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        
        # act
        response = self.client.get('/memo/messages/details/' + str(m.pk))
        
        # assert
        self.assertContains(response, str(m.latitude))
        self.assertContains(response, str(m.longitude))
        self.assertContains(response, str(m.altitude))
        self.assertContains(response, str(m.accuracy))
