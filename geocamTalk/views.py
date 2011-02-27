# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from geocamMemo.models import GeocamMessage
from geocamTalk.forms import GeocamTalkForm
import json

@login_required
def message_list(request):
    
    messages = GeocamMessage.objects.all().order_by( 'content_timestamp').reverse()

    return render_to_response('geocamTalk/messagelist.html', 
                              {"gc_msg": messages}, context_instance=RequestContext(request))

@login_required
def feedMessages(request):
    ordered_messages = GeocamMessage.objects.all().order_by('-content_timestamp')
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
            form.save()        
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