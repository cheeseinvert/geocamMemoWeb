# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from geocamMemo.models import GeocamMessage, get_user_string
from django.contrib.auth.models import User
from django.db.models import Q, Count

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
    
    def getJson(self):
          return  dict(messageId=self.pk,
                       authorUsername=self.author.username,
                       authorFullname=self.get_author_string(),
                       recipients=[r.username for r in self.recipients.all()],
                       content=self.content, 
                       content_timestamp=self.get_date_string(),
                       latitude=self.latitude,
                       longitude=self.longitude,
                       accuracy=self.accuracy,
                       has_geolocation=bool(self.has_geolocation()) )
    
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
          
