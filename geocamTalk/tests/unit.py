# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from geocamTalk.models import TalkMessage
from django.core.files.base import ContentFile
import array, os, random
import string
import time


class GeocamTalkUnitTest(TestCase):
    fixtures = ['demoTalkMessages.json', 'demoUsers.json']
    
    def setUp(self):
        self.now = datetime.now()
    
    def testEnsureRecipientsCanBeAddedToAMessage(self):
        # arrange
        sender = User.objects.all()[0]
        recipienta = User.objects.all()[1]
        recipientb = User.objects.all()[2]

        # act
        message = TalkMessage.objects.create(
            content="012345678901234567890123456789", 
            content_timestamp=self.now, 
            author=sender)
            
        message.recipients.add(recipienta)
        message.recipients.add(recipientb)
        
        # assert
        self.assertEquals(2, len(message.recipients.all()), "All recipients should be added to the message")
    
    def testCanStoreAudioMessage(self):
        #arrange
        sender = User.objects.all()[0]
        
        #act
        no_audio_message = TalkMessage.objects.create(
            content="012345678901234567890123456789", 
            content_timestamp=self.now,
            audio_file='', 
            author=sender)
        
        
        
        audio_message = TalkMessage.objects.create(
            audio_file="audiofile.mp4",
            content_timestamp=self.now, 
            author=sender)
                    
        #assert
        self.assertFalse(no_audio_message.has_audio())
        self.assertTrue(audio_message.has_audio())
        

class TalkUserProfileUnitTest(TestCase):
    fixtures = ['demoTalkMessages.json', 'demoUsers.json']
            
    def testEnsureLastViewedMyMessages(self):
        # arrange
        user = User.objects.all()[0]
        latestmsgId = TalkMessage.getLargestMessageId()
        profile = user.profile
        
        # act
        profile.last_viewed_mymessages = latestmsgId
        profile.save()
        
        # assert
        self.assertEquals(latestmsgId,user.profile.last_viewed_mymessages)
        
    def testCanGetUnreadMessageCount(self):
        # arrange
        user = User.objects.all()[0]
        profile = user.profile
        
        currentCount = profile.getUnreadMessageCount()
        
        # act
        TalkMessage.objects.create(
            content="012345678901234567890123456789", 
            content_timestamp=datetime.now(), 
            author=user)
                
        # assert
        self.assertEquals(currentCount + 1, profile.getUnreadMessageCount())

    def testEnsureFromJsonCreatesMessage(self):        
        #arrange
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        hour = now.strftime("%H")
        min = now.strftime("%H")
        sec = now.strftime("%H")
        
        timestamp = datetime(int(year), int(month), int(day), int(hour), int(min), int(sec))

        message = dict(                    
                    userId=User.objects.all()[0].pk,
                    content="Sting!!!",
                    contentTimestamp=time.mktime(timestamp.timetuple()) * 1000,
                    latitude=1.1,
                    longitude=222.2,
                    accuracy=60 )
        
        audioFile = 'media/geocamTalk/test/%s/%s/%s/test_ensure_from_json.mp4' % (year,month,day)
        self._createFile(filename=audioFile, filesize=100*1024)
        f = open(audioFile, "rb")
        #act
        talkMessage = TalkMessage.fromJson(message)
        talkMessage.audio_file.save(f.name, ContentFile(f.read()))
        talkMessage.save()
            
        #assert
        self.assertEqual(talkMessage.author.pk, User.objects.all()[0].pk)
        self.assertEqual(talkMessage.content, "Sting!!!")
        self.assertEqual(talkMessage.content_timestamp, timestamp)
        self.assertEqual(talkMessage.latitude, 1.1)
        self.assertEqual(talkMessage.longitude, 222.2)
        self.assertEqual(talkMessage.accuracy, 60)
        self.assertTrue(talkMessage.has_audio())
        self.assertEqual(os.path.basename(talkMessage.audio_file.name), os.path.basename(f.name))
        f.close()
        self._clean_test_files(audioFile)
         
        
    def _createFile(self, filename, filesize=5*1024*1024):
        """Create and fill a file with random data"""
        blocksize = 4096 # 4k
        datablock = array.array('I')
        written = 0
        # Create a datablock:
        while written < blocksize:
            datablock.append(random.getrandbits(32))
            written = written + 4
        
        test_folder = os.path.dirname(filename)
        post_folder = string.replace(test_folder, "test", "audio", 1)
        try:
            os.makedirs(test_folder)
        except:
            pass
        try:
            os.makedirs(post_folder)
        except:
            pass
        with open(filename, 'w') as f:
            written = 0
            while written < filesize:
                datablock.tofile(f)
                written += blocksize
            f.flush()
            os.fsync(f.fileno())
            
    def _clean_test_files(self, test_file_path):
        filename = os.path.basename(test_file_path)
        test_folder = os.path.dirname(test_file_path)
        post_folder = string.replace(test_folder,"test", "audio", 1)
        
        post_file_path = os.path.join(post_folder, filename)
        os.unlink(post_file_path)
        for the_file in os.listdir(test_folder):
            file_path = os.path.join(test_folder, the_file)
            try:
                os.unlink(file_path)
            except Exception, e:
                print e