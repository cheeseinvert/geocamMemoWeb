# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.simple import redirect_to
from django import forms
from geocamMemo.models import MemoMessage, get_user_string
from geocamMemo.forms import MemoMessageForm
from datetime import datetime
import json

def get_first_geolocation(messages):
    """ return the first geotagged message lat and long as tuple """
    
    try:
        return [(m.latitude, m.longitude) for m in messages if m.has_geolocation()][0]
    except:
        return ()

@login_required
def message_map(request):
    messages = MemoMessage.getMessages()
    return render_to_response('geocamMemo/map.html',
                              dict(gc_msg=messages,
                                   first_geolocation=get_first_geolocation(messages)),
                              context_instance=RequestContext(request))

@login_required
def message_list(request, author_username=None):
    if author_username is not None:
        author = get_object_or_404(User, username=author_username)
    else:
        author = None 
    return render_to_response('geocamMemo/message_list.html', 
                              dict(gc_msg=MemoMessage.getMessages(author),
                                   author=author), 
                              context_instance=RequestContext(request))

# manual not logged in response
def message_list_json(request):
    if request.user.is_authenticated():        
        messages = MemoMessage.getMessages()
        return HttpResponse(json.dumps([msg.getJson() for msg in messages]))
    else:
        return HttpResponseForbidden()

@login_required
def index(request):
    return HttpResponseRedirect(reverse('memo_message_list_all'))
    
@login_required
def message_details(request, message_id):
    message = get_object_or_404(MemoMessage, pk=message_id)
            
    return render_to_response('geocamMemo/details.html',
                              {'message':message},
                              context_instance=RequestContext(request))
# login not yet required
def message_details_json(request, message_id):
    message = get_object_or_404(MemoMessage, pk=message_id)
    return HttpResponse(json.dumps(message.getJson()))

@login_required
def create_message(request):
    if request.method == 'POST':
        form = MemoMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            # Since revisions are now saved to db, this timestamp
            # can't just be auto set since we want to preserve from creation time
            msg.content_timestamp = datetime.now()
            msg.save()
            return HttpResponseRedirect(reverse('memo_message_list_all'))
        else:
            return render_to_response('geocamMemo/message_form.html',
                                  dict(form=form),
                                  context_instance=RequestContext(request))
    else:
        form = MemoMessageForm()
        return render_to_response('geocamMemo/message_form.html',
                                  dict(form=form),                                   
                                  context_instance=RequestContext(request))

def create_message_json(request):    
    if request.user.is_authenticated():
        if request.method == 'POST':
            jsonstring = request.POST["message"]
            messageDict = json.loads(jsonstring)
            messageDict["userId"] = request.user.pk
            message = MemoMessage.fromJson(messageDict)
            try:
                message.save()
                return HttpResponse("", 200) 
            except:
                return HttpResponseServerError()
        else:
               return HttpResponseServerError()
    else:
        return HttpResponseForbidden()
  
@login_required
def edit_message(request, message_id):
    message = MemoMessage.objects.get(pk=message_id)
    if message.author.username != request.user.username and not request.user.is_superuser:
        return HttpResponseRedirect(reverse('memo_message_list_all')) # you get the boot!
    if request.method == 'POST':
        message.content = request.POST['content']
        form = MemoMessageForm(request.POST)   
        if form.is_valid():
            message.save()
            return HttpResponseRedirect(reverse('memo_message_list_all'))
        else:
            return render_to_response('geocamMemo/edit_message_form.html',
                                  dict(form=form,
                                       message=message),
                                  context_instance=RequestContext(request))      
    else:
        form = MemoMessageForm(instance=message)
        return render_to_response('geocamMemo/edit_message_form.html',                                  
                                  dict(form=form,
                                       message=message),                                  
                                  context_instance=RequestContext(request))\

@login_required
def delete_message(request, message_id):
    message = MemoMessage.objects.get(pk=message_id)
    if message.author.username == request.user.username or request.user.is_superuser:
        message.delete()
    return HttpResponseRedirect(reverse('memo_message_list_all'))
