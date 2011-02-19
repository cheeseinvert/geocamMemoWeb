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
