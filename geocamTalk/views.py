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
def message_list(request, recipient_username=None, author_username=None):
    
    allOfMyMessages = set()
    messages = []
    author = None
    recipient = None
    if(recipient_username == None):    
        messages = get_latest_message_revisions(TalkMessage)
    elif (author_username == None):
        recipient = get_object_or_404(User, username=recipient_username)      
        for to_me in recipient.received_messages.all(): # messages to me
            allOfMyMessages.add(to_me)
        for from_me in  recipient.geocamtalk_talkmessage_set.all():# messages from me
            allOfMyMessages.add(from_me)
        for broadcast in TalkMessage.objects.all(): # broadcast messages
            if(broadcast.recipients.count() == 0):            
                allOfMyMessages.add(broadcast)
                
        messages = list(allOfMyMessages)
    else:
        recipient_messages_from_author_or_broadcast = set()
        recipient = get_object_or_404(User, username=recipient_username)  
        author = get_object_or_404(User, username=author_username)         
        for m in recipient.received_messages.all(): # messages to me
            allOfMyMessages.add(m)
        for m in TalkMessage.objects.all(): # broadcast messages
            if(m.recipients.count() == 0):            
                allOfMyMessages.add(m)
        for m in allOfMyMessages: #filter messages by author
            if (m.author == author):
                recipient_messages_from_author_or_broadcast.add(m)   
        messages = list(recipient_messages_from_author_or_broadcast)
        
    messages = sorted(messages, cmpMessageSortNewestFirst)

    return render_to_response('geocamTalk/messagelist.html', 
                              {"gc_msg": messages, "recipient": recipient, "author": author}, context_instance=RequestContext(request))

def cmpMessageSortNewestFirst(message1, message2):
    if(message1.content_timestamp > message2.content_timestamp):
        return -1
    if(message1.content_timestamp == message2.content_timestamp):
        return 0
    else:
        return 1

@login_required
def feedMessages(request, recipient_username=None, author_username=None):
    
    allOfMyMessages = set() 
    ordered_messages = []
    if(recipient_username == None):    
        ordered_messages = get_latest_message_revisions(TalkMessage)
        
    elif(author_username == None):
        recipient = get_object_or_404(User, username=recipient_username)      
        for to_me in recipient.received_messages.all(): # messages to me
            allOfMyMessages.add(to_me)
        for from_me in  recipient.geocamtalk_talkmessage_set.all():# messages from me
            allOfMyMessages.add(from_me)
        for broadcast in TalkMessage.objects.all(): # broadcast messages
            if(broadcast.recipients.count() == 0):            
                allOfMyMessages.add(broadcast)
        ordered_messages = list(allOfMyMessages)
    else:
        recipient_messages_from_author_or_broadcast = set()
        recipient = get_object_or_404(User, username=recipient_username)
        author = get_object_or_404(User, username=author_username)      
        for m in recipient.received_messages.all(): # messages to me
            allOfMyMessages.add(m)
        for m in TalkMessage.objects.all(): # broadcast messages
            if(m.recipients.count() == 0):            
                allOfMyMessages.add(m)
        for m in allOfMyMessages: #filter messages by author
            if (m.author == author):
                recipient_messages_from_author_or_broadcast.add(m)   
        ordered_messages = list(recipient_messages_from_author_or_broadcast)
        
    ordered_messages = sorted(ordered_messages, cmpMessageSortNewestFirst)

    stringified_msg_list = [{'pk':msg.pk,
                             'author':msg.get_author_string(), 
                             'recipients':msg.get_recipients_string(),
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