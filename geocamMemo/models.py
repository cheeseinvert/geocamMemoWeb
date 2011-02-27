# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from django.contrib.auth.models import User

class GeocamMessage(models.Model):
    """ This is the data model for geocam messages """
    
    author = models.ForeignKey(User)
    content = models.TextField(max_length=1024)
    content_timestamp = models.DateTimeField(auto_now_add=True)
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
