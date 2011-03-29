# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from geocamMemo.models import MemoMessage, get_user_string
from django.core.urlresolvers import reverse


class GeocamMemoListViewTest(TestCase):
    fixtures = ['demoUsers.json', 'demoMemoMessages.json']
    
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
        displayed_message_ids = [m.pk for m in displayedmessages]
        
        messages = MemoMessage.getMessages() #descending (newest at top)
        message_ids = [m.pk for m in messages] 

        self.assertEqual(displayed_message_ids, message_ids, "Order should be the same")

    def testMessageListDateFormat(self):
        messages = MemoMessage.latest.all()
        response = self.get_messages_response()
        for m in messages:
            self.assertContains(response, m.content_timestamp.strftime("%m/%d/%y %H:%M:%S"), None, 200)
        
    def testMessageListAuthorFormat(self):
        messages = MemoMessage.latest.all()
        response = self.get_messages_response()
        
        for m in messages:
            if m.author.first_name:
              self.assertContains(response, m.author.first_name + " " + m.author.last_name)
            else:
              self.assertContains(response, m.author.username)
        
    def testMessageListContentFormat(self):
        
        messages = MemoMessage.latest.all()
        response = self.get_messages_response()
        for m in messages:
            self.assertContains(response, m.content)
    
    def testMessageListGeoLocationPresent(self):
        # arrange
        response = self.get_messages_response()

        # act
        geocount = MemoMessage.latest.exclude(latitude=None, longitude=None).count()
        
        # assert
        self.assertContains(response, "data-icon=\"geoCam-map\"", geocount)
        self.assertContains(response, 'data-rel="dialog"', geocount)
        
    def testEnsureMessagesAreFilteredByUser(self):
        # arrange
        user = User.objects.all()[1]
        messages = MemoMessage.objects.filter(author=user.pk)
        
        notUserMessages = MemoMessage.objects.exclude(author=user.pk)
        
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
        messages = MemoMessage.getMessages(u) 
        message_ids = [m.pk for m in messages]  
        
        #act
        response = self.get_messages_response_filtered(u)

        #Looks at last parameter of context. Denoted by -1
        displayedmessages = response.context[-1]['gc_msg'] # get the data object sent to the template
        displayed_message_ids = [m.pk for m in displayedmessages] 
        
        #assert
        self.assertEqual(displayed_message_ids, message_ids, "Order should be the same")
 
    def testEnsureMessageListAuthorLinksPresent(self):
        #arrange        
        messages = MemoMessage.latest.all()
        
        #act
        response = self.get_messages_response()
        
        #assert
        for m in messages:            
            self.assertContains(response, 'href="' + reverse("memo_message_list_user", args=[m.author.username]))
    
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
        response = self.client.get(reverse("memo_message_list_user", args=[user.username]))
        return response
    
    def get_messages_response(self):
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self.client.get(reverse("memo_message_list_all"))
        return response

class GeocamMemoMapViewTest(TestCase):
    fixtures = ['demoUsers.json', 'demoMemoMessages.json']


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
        messages = MemoMessage.getMessages()
        assert not messages[0].has_geolocation(), "Fixtures should have a non-geolocated message as latest"
        
        #let's find the first message that has a geoloction and ensure the map is centered on it 
        message = None
        for m in messages:
            if m.has_geolocation():
                message = m
                break 
            
        lat = message.latitude
        lon = message.longitude

        #act
        response = self.get_map_response()
        
        #assert
        self.assertContains(response, "createMap("+str(lat)+","+str(lon)+")")
        self.assertContains(response, "<section id=\"map_canvas\"")
        for m in messages:
            if m.has_geolocation():
                self.assertContains(response, "latitude:"+str(m.latitude))
            else:
                self.assertNotContains(response, "google.maps.LatLng("+str(m.latitude)+","+str(m.longitude)+")")
                
    def get_map_response(self):
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        response = self.client.get(reverse("memo_message_map"))
        return response

class GeocamMemoSingleMessageViewTest(TestCase):
    fixtures = ['demoUsers.json', 'demoMemoMessages.json']

    def testEnsureProperFieldsAreDisplayed(self):
        # arrange
        m = MemoMessage.latest.all()[0]
        
        u = User.objects.all()[0]
        self.client.login(username=u.username, password='geocam')
        
        # act
        response = self.client.get(reverse("memo_message_details", args=[m.pk]))
        
        # assert
        self.assertContains(response, str(m.latitude))
        self.assertContains(response, str(m.longitude))
        self.assertContains(response, str(m.altitude))
        self.assertContains(response, str(m.accuracy))
