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

class GeocamMessage(revisions.models.VersionedModel):
    """ This is the data model for geocam messages 
    
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
    
    author = models.ForeignKey(User)
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
        return self.content_timestamp.strftime("%m/%d %H:%M:%S")
    
    def get_author_string(self):
        return get_user_string(self.author)
    
    def title(self):
        return self.content[:16] + "..." if len(self.content) > 19 else self.content
          
    def has_geolocation(self):
        return bool(self.latitude != None and self.longitude != None)

    def __unicode__(self):
        return "Message from %s on %s: %s" % (self.author.username, self.content_timestamp, self.content)

def get_user_string(user):
    if user.first_name and user.last_name:
        return (user.first_name + " " + user.last_name)
    else:
        return (user.username)

def get_latest_message_revisions():
    """ Returns a query set of the latest revisions of all message objects """
    messages = []
    allMsgs = GeocamMessage.objects.all().order_by('-content_timestamp')
    for msg in allMsgs:
        if msg.check_if_latest_revision():
            messages.append(msg)
    return messages
    