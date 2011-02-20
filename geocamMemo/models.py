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
        if self.author.first_name:
              return (self.author.first_name + " " + self.author.last_name)
        else:
              return (self.author.username)
          
    def has_geolocation(self):
        return (self.latitude and self.longitude)

    def __unicode__(self):
        return "Message from %s %s" % (self.author.username, self.content)
