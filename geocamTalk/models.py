# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from geocamMemo.models import GeocamMessage,get_user_string
from django.contrib.auth.models import User

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
    def __unicode__(self):
        try:
            str = "Talk message from %s to %s on %s: %s" % (self.author.username, self.recipients.all(), self.content_timestamp, self.content)
        except:
            str = "Talk message from %s on %s: %s" % (self.author.username, self.content_timestamp, self.content)
        return str
    
    recipients = models.ManyToManyField(User, null=True, blank=True, related_name="received_messages")
    
    def get_recipients_string(self):
        recipient_string = ""
        for r in self.recipients.all():
            try:  
                recipient_string += ',"%s"' % get_user_string(r)               
            except:
                recipient_string = '"%s"' % get_user_string(r)                       
        return '[%s]' % recipient_string