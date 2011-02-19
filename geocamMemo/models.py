# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from django.contrib.auth.models import User

class GeocamMessage(models.Model):
    """ This is the data model for geocam messages """
    
    content = models.CharField(max_length=1024)
    lat = models.FloatField()
    lon = models.FloatField()
    author = models.ForeignKey(User)
    create_date = models.DateTimeField()
    
    def get_date_string(self):
        return self.create_date.strftime("%m/%d %H:%M:%S")
    
    def get_author_string(self):
        if self.author.first_name:
              return (self.author.first_name + " " + self.author.last_name)
        else:
              return (self.author.username)
          
    def has_geolocation(self):
        return (self.lat and self.lon)
