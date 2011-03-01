# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from geocamMemo.models import GeocamMessage

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
        return "Talk message from %s on %s: %s" % (self.author.username, self.content_timestamp, self.content)