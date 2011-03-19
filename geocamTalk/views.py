# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from geocamTalk.models import TalkMessage
from geocamMemo.models import get_latest_message_revisions, get_user_string
from geocamTalk.forms import GeocamTalkForm
from datetime import datetime
from django.contrib.auth.models import User
import json

@login_required
def message_list(request, username=None):
    
    if(username == None):    
        messages = get_latest_message_revisions(TalkMessage)
    else:
        user = get_object_or_404(User, username=username)
        allOfMyMessages = set()        
        for to_me in user.received_messages.all(): # messages to me
            allOfMyMessages.add(to_me)
        for from_me in  user.geocamtalk_talkmessage_set.all():# messages from me
            allOfMyMessages.add(from_me)
        for broadcast in TalkMessage.objects.all(): # broadcast messages
            if(broadcast.recipients.count() == 0):            
                allOfMyMessages.add(broadcast)
        
        messages = list(allOfMyMessages)
        messages = sorted(messages, cmpMessageSortNewestFirst)

    return render_to_response('geocamTalk/messagelist.html', 
                              {"gc_msg": messages, "username": username}, context_instance=RequestContext(request))

def cmpMessageSortNewestFirst(message1, message2):
    if(message1.content_timestamp > message2.content_timestamp):
        return -1
    if(message1.content_timestamp == message2.content_timestamp):
        return 0
    else:
        return 1

@login_required
def feedMessages(request, username=None):
    
    if(username == None):    
        ordered_messages = get_latest_message_revisions(TalkMessage)
    else:
        user = get_object_or_404(User, username=username)
        allOfMyMessages = set()        
        for to_me in user.received_messages.all(): # messages to me
            allOfMyMessages.add(to_me)
        for from_me in  user.geocamtalk_talkmessage_set.all():# messages from me
            allOfMyMessages.add(from_me)
        for broadcast in TalkMessage.objects.all(): # broadcast messages
            if(broadcast.recipients.count() == 0):            
                allOfMyMessages.add(broadcast)
        
        ordered_messages = list(allOfMyMessages)
        ordered_messages = sorted(ordered_messages, cmpMessageSortNewestFirst)

    stringified_msg_list = [{'pk':msg.pk,
                             'author':msg.get_author_string(), 
                            'content':msg.content, 
                            'content_timestamp':msg.get_date_string(),
                            'has_geolocation':bool(msg.has_geolocation()) } for msg in ordered_messages ]
    return HttpResponse(json.dumps(stringified_msg_list))
    
@login_required
def index(request):
    return render_to_response('geocamTalk/home.html',
                              {}, context_instance=RequestContext(request))

@login_required
def create_message(request):
    if request.method == 'POST':
        form = GeocamTalkForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            # Since revisions are now saved to db, this timestamp
            # can't just be auto set since we want to preserve from creation time
            msg.content_timestamp = datetime.now()
            msg.save()
            form.save_m2m()
            return HttpResponseRedirect('/talk/messages/')
        else:
            return render_to_response('geocamTalk/message_form.html',
                                  {'form':form},
                                  context_instance=RequestContext(request))
    else:
        form = GeocamTalkForm()
        return render_to_response('geocamTalk/message_form.html',
                                  {'form':form },                                   
                                  context_instance=RequestContext(request))