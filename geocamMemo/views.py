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
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.simple import redirect_to
from django import forms
from geocamMemo.models import GeocamMessage, get_user_string, get_latest_message_revisions
from geocamMemo.forms import GeocamMessageForm
from datetime import datetime

@login_required
def message_list(request):
    messages = get_latest_message_revisions()
    
    return render_to_response('geocamMemo/messagelist.html', 
                               
                              {"gc_msg": messages,
                               "first_geolocation":get_first_geolocation(messages)
                               }, context_instance=RequestContext(request))

@login_required
def message_list_filtered_username(request, username):
    user = get_object_or_404(User, username=username)
    
    messages = GeocamMessage.objects.filter(author = user.pk).order_by('-content_timestamp')
    return render_to_response('geocamMemo/messagelist.html', 
                              {"gc_msg": messages,
                               "first_geolocation":get_first_geolocation(messages),
                               "userstring": get_user_string(user)}, context_instance=RequestContext(request))

def get_first_geolocation(messages):
    i = 0
    if len(messages):
        while (i < len(messages)-1) and not messages[i].has_geolocation():
            i += 1
        return [ messages[i].latitude, messages[i].longitude ]
    else:
        return []

@login_required
def index(request):
    return render_to_response('geocamMemo/home.html',
                              {}, context_instance=RequestContext(request))
    
@login_required
def details(request, message_id):
    message = get_object_or_404(GeocamMessage, pk = message_id)
    if request.is_ajax():
        template_to_extend = 'geocamMemo/base_ajax.html'
    else:
        template_to_extend = 'geocamMemo/base.html'
            
    return render_to_response('geocamMemo/details.html',
                              {'message':message},
                              context_instance=RequestContext(request))

@login_required
def create_message(request):
    if request.method == 'POST':
        form = GeocamMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            # Since revisions are now saved to db, this timestamp
            # can't just be auto set since we want to preserve from creation time
            msg.content_timestamp = datetime.now()
            msg.save()
            return HttpResponseRedirect('/memo/messages/')
        else:
            return render_to_response('geocamMemo/message_form.html',
                                  {'form':form},
                                  context_instance=RequestContext(request))
    else:
        form = GeocamMessageForm()
        return render_to_response('geocamMemo/message_form.html',
                                  {'form':form },                                   
                                  context_instance=RequestContext(request))

@login_required
def edit_message(request, message_pk):
    message = GeocamMessage.objects.get(pk=message_pk)
    if message.author.pk != request.user.pk and not request.user.is_superuser:
        return HttpResponseRedirect('/memo/messages/') # you get the boot!
    if request.method == 'POST':
        message.content = request.POST['content']
        form = GeocamMessageForm(request.POST)   
        if form.is_valid():
            message.save()
            return HttpResponseRedirect('/memo/messages/')
        else:
            return render_to_response('geocamMemo/edit_message_form.html',
                                  {'form':form,
                                   'message':message},
                                  context_instance=RequestContext(request))      
    else:
        form = GeocamMessageForm(instance=message)
        return render_to_response('geocamMemo/edit_message_form.html',                                  
                                  {'form':form, 
                                   'message':message},                                   
                                  context_instance=RequestContext(request))\

@login_required
def delete_message(request, message_pk):
    message = GeocamMessage.objects.get(pk=message_pk)
    if message.author.pk == request.user.pk or request.user.is_superuser:
        message.delete()
    return HttpResponseRedirect('/memo/messages/')