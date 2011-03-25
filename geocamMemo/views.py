# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.simple import redirect_to
from django import forms
from geocamMemo.models import MemoMessage, get_user_string
from geocamMemo.forms import MemoMessageForm
from datetime import datetime

@login_required
def memo_map(request):
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

def get_first_geolocation(messages):
    """ return the first geotagged message lat and long as tuple """
    
    try:
        return [(m.latitude, m.longitude) for m in messages if m.has_geolocation()][0]
    except:
        return ()

@login_required
def index(request):
    return HttpResponseRedirect(reverse('all_message_list'))
    
@login_required
def details(request, message_id):
    message = get_object_or_404(MemoMessage, pk=message_id)
            
    return render_to_response('geocamMemo/details.html',
                              {'message':message},
                              context_instance=RequestContext(request))

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
            return HttpResponseRedirect(reverse('all_message_list'))
        else:
            return render_to_response('geocamMemo/message_form.html',
                                  dict(form=form),
                                  context_instance=RequestContext(request))
    else:
        form = MemoMessageForm()
        return render_to_response('geocamMemo/message_form.html',
                                  dict(form=form),                                   
                                  context_instance=RequestContext(request))

@login_required
def edit_message(request, message_id):
    message = MemoMessage.objects.get(pk=message_id)
    if message.author.username != request.user.username and not request.user.is_superuser:
        return HttpResponseRedirect(reverse('all_message_list')) # you get the boot!
    if request.method == 'POST':
        message.content = request.POST['content']
        form = MemoMessageForm(request.POST)   
        if form.is_valid():
            message.save()
            return HttpResponseRedirect(reverse('all_message_list'))
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
    return HttpResponseRedirect(reverse('all_message_list'))