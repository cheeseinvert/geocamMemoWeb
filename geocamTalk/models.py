# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from geocamMemo.models import GeocamMessage, get_user_string
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import datetime
import time, sys
from django.db.models import Q, Count
import httplib
import urllib
from geocamMemo.authentication import GOOGLE_TOKEN

class TalkUserProfile(models.Model):
    user = models.ForeignKey(User, related_name='profile')
    last_viewed_mymessages = models.IntegerField(default=0)
    registration_id = models.CharField(max_length=128)
    
    def getUnreadMessageCount(self):
        return TalkMessage.getMessages(self.user).filter(
                                        pk__gt=self.last_viewed_mymessages).count()

User.profile = property(lambda u: TalkUserProfile.objects.get_or_create(user=u)[0])

class TalkMessage(GeocamMessage):
    """ This is the data model for Memo application messages 
    
    Some of the Versioned Model API:
        VersionedModel.get_latest_revision()
        VersionedModel.get_revisions()
        VersionedModel.make_current_revision()
        VersionedModel.revert_to(criterion)
        VersionedModel.save(new_revision=True, *vargs, **kwargs)
        VersionedModel.show_diff_to(to, field)
    complete API and docs are here: 
    http://stdbrouw.github.com/django-revisions/

    """
    #TODO - add time to filename location
    audio_file = models.FileField(null=True, blank=True, upload_to='geocamTalk/audio/%Y/%m/%d') #"%s-audio" % (GeocamMessage.author))
    
    def __unicode__(self):
        try:
            str = "Talk message from %s to %s on %s: %s" % (self.author.username, self.recipients.all(), self.content_timestamp, self.content)
        except:
            str = "Talk message from %s on %s: %s" % (self.author.username, self.content_timestamp, self.content)
        return str
    
    recipients = models.ManyToManyField(User, null=True, blank=True, related_name="received_messages")
    
    def getJson(self):
          return  dict(messageId=self.pk,
                       userId=self.author.pk,
                       authorUsername=self.author.username,
                       authorFullname=self.get_author_string(),
                       recipients=[r.username for r in self.recipients.all()],
                       content=self.content, 
                       contentTimestamp=self.get_date_string(),
                       latitude=self.latitude,
                       longitude=self.longitude,
                       accuracy=self.accuracy,
                       audioUrl=self.get_audio_url(),
                       hasGeolocation=bool(self.has_geolocation()) )
    
    @staticmethod
    def fromJson(messageDict):
        print "inside fromJson!\n"
        message = TalkMessage()    
        if "content" in messageDict:
            message.content = messageDict["content"]   
        if "contentTimestamp" in messageDict:
            time_format = "%m/%d/%y %H:%M:%S"
            message.content_timestamp = datetime.datetime.fromtimestamp(time.mktime(time.strptime(messageDict["contentTimestamp"], time_format)))             
        if "latitude" in messageDict:
            message.latitude = messageDict["latitude"]
        if "longitude" in messageDict:
            message.longitude = messageDict["longitude"]
        if "accuracy" in messageDict:
            message.accuracy = messageDict["accuracy"]                               
        if "userId" in messageDict:
            message.author_id = messageDict["userId"]
        if "recipientUsername" in messageDict:
            print "inside the iff satetment!\n"
            r = User.objects.get(username=messageDict["recipientUsername"])
            print "recipient is %s" % r
            print "message is %s" % message
            message.save()
            message.recipients.add(r)
            print "dont think I'll see this part...\n"         
        return message  
    
    @staticmethod
    def getMessages(recipient=None, author=None):
        """ Message Listing Rules:
        
        If no users are specified: all messages are displayed (latest revisions)
        If only author is specified: all messages are displayed from author
        If only recipient is specified: messages displayed are broadcast + from OR to recipient
        If both recipient AND author are specified: messages displayed are braodcast + from author AND to recipient
        
        Note: a broadcast message is a message with no recipients
        """
        if (recipient is None and author is None):
            # all messages are displayed (latest revisions)    
            messages = TalkMessage.latest.all()
        elif (recipient is None and author is not None):
            # messages displayed are from author:
            messages = TalkMessage.latest.filter(author__username=author.username)   
        elif (recipient is not None and author is None):
            # messages displayed are broadcast + from OR to recipient:
            messages = TalkMessage.latest.annotate(num_recipients=Count('recipients')).filter(Q(num_recipients=0) | Q(recipients__username=recipient.username) | Q(author__username=recipient.username)).distinct()       
        else: 
            # messages displayed are braodcast + from author AND to recipient
            messages = TalkMessage.latest.annotate(num_recipients=Count('recipients')).filter(Q(num_recipients=0) | Q(recipients__username=recipient.username)).filter(author__username=author.username).distinct()         
        return messages.order_by('-content_timestamp')
    
    @staticmethod
    def getLargestMessageId():
        return TalkMessage.objects.all().order_by('-pk')[0].pk
    
    def has_audio(self):
        return bool(self.audio_file != '')   
            
    def push_to_phone(self, pushToSender = True):
        message = self
    
        # NOW SEND THE REQUEST TO GOOGLE SERVERS
        # first we need an https connection that ignores the certificate (for now)
        httpsconnection = httplib.HTTPSConnection("android.apis.google.com", 443)
    
        push_recipients = self.recipients.all()
        if(push_recipients.count() == 0):
            push_recipients = User.objects.all();
        
        for user in push_recipients:
            if(user.profile.registration_id):
                if(pushToSender or user.pk != message.author.pk):
                    # we need the following params set per http://code.google.com/android/c2dm/index.html#push
                    params = urllib.urlencode({
                             'registration_id': user.profile.registration_id,
                             'collapse_key': "message"+str(message.pk),
                             'data.message_id': str(message.pk),
                             'delay_when_idle':'TRUE',
                             })
            
                    # need the following headers set per http://code.google.com/android/c2dm/index.html#push
                    headers = { "Content-Type":"application/x-www-form-urlencoded",
                                "Content-Length":len(params),
                                "Authorization":"GoogleLogin auth=" + GOOGLE_TOKEN # TOKEN set manually in authentication.py
                                }
                    
                    httpsconnection.request("POST", "/c2dm/send", params, headers)

    def get_audio_url(self):
        if self.audio_file:
            return self.audio_file.url
        else:
            return None
