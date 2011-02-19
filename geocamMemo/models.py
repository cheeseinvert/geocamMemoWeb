# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm

class GeocamMessage(models.Model):
    """ This is the data model for geocam messages """
    
    content = models.TextField(max_length=1024)
    lat = models.FloatField()
    lon = models.FloatField()
    author = models.ForeignKey(User)
    create_date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "Message from %s %s" % (self.author.username, self.content)
    

class GeocamMessageForm(ModelForm):
    class Meta:
        model = GeocamMessage
