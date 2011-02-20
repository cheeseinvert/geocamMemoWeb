# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django import forms
from geocamMemo.models import GeocamMessage
from datetime import datetime
import re

class GeolocationTimestampDateTimeFormField(forms.DateTimeField):
    def clean(self, value):
        """ datetime from geolocation timestamp 
        ex: Sat Feb 19 2011 15:37:53 GMT-0800 (PST)"""
        
        #=======================================================================
        try:
            if value is None or value == "":
                return ""
            clean_date = re.match(r"(\S+ \S+ \d+ \d+ \d+\:\d+\:\d+)", 
                                  value).group(1)
            dt = datetime.strptime(clean_date, "%a %b %d %Y %H:%M:%S")
            return dt
        except:
            raise forms.ValidationError
        #=======================================================================
            
class GeocamMessageForm(forms.ModelForm):
    position_timestamp = GeolocationTimestampDateTimeFormField()
    class Meta:
        model = GeocamMessage
