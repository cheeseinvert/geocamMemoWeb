# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from django.contrib.auth.models import User
from revisions.models import VersionedModel
from revisions.shortcuts import VersionedModel as VersionedModelShortcuts
import revisions
import json
import time, datetime
from geocamMemo import authentication

class GeocamMessage(revisions.models.VersionedModel):
    """ This is the abstract data model for geocam messages 
    
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
    
    class Meta:
        abstract = True
    
    server_timestamp = models.DateTimeField(auto_now_add = True)
    author = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_set")
    content = models.TextField(max_length=1024)
    # removed auto_add_now from content_timestamp since revisions are also instances in the 
    # same table and we don't overwrite this timestamp on an edit
    content_timestamp = models.DateTimeField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    heading = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    position_timestamp = models.DateTimeField(null=True, blank=True)
    
    def get_date_string(self):
        return self.content_timestamp.strftime("%m/%d/%y %H:%M:%S")
    
    def get_author_string(self):
        return get_user_string(self.author)
    
    def title(self):
        return self.content[:16] + "..." if len(self.content) > 19 else self.content
          
    def has_geolocation(self):
        return bool(self.latitude != None and self.longitude != None)

    pass

class MemoMessage(GeocamMessage):
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
    def __unicode__(self):
        return "Memo from %s on %s: %s" % (self.author.username, self.content_timestamp, self.content)
    
    def getJson(self):
        return  dict(
                    messageId=self.pk,
                    userId=self.author.pk,
                    authorUsername=self.author.username,
                    authorFullname=self.get_author_string(), 
                    content=self.content,
                    contentTimestamp=self.get_date_string(),
                    latitude=self.latitude,
                    longitude=self.longitude,
                    accuracy=self.accuracy,
                    hasGeolocation=bool(self.has_geolocation()) )
    
    @staticmethod
    def fromJson(messageDict):
        message = MemoMessage()    
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
        return message            
        
    @staticmethod
    def getMessages(author=None):
        """ Message Listing Rules:
        
        If no author is specified: all messages are displayed (latest revisions)
        If author is specified: all messages are displayed from author
        """
        
        if (author is None):
            # all messages are displayed (latest revisions)    
            messages = MemoMessage.latest.all()
        else:
            # messages displayed are from author:
            messages = MemoMessage.latest.filter(author__username=author.username)   
        return messages.order_by('-content_timestamp')

def get_user_string(user):
    if user.first_name and user.last_name:
        return (user.first_name + " " + user.last_name)
    else:
        return (user.username)

User.full_name = property(lambda u: get_user_string(u))

