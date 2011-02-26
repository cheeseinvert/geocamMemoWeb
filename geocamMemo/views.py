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
from geocamMemo.models import GeocamMessage, get_user_string
from geocamMemo.forms import GeocamMessageForm

@login_required
def message_list(request):
    messages = GeocamMessage.objects.order_by('-content_timestamp')
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
    while (i < len(messages)-1) and not messages[i].has_geolocation():
        i += 1
    return [ messages[i].latitude, messages[i].longitude ]

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
                              {'message':message,'template_to_extend':template_to_extend},
                              context_instance=RequestContext(request))

@login_required
def create_message(request):
    if request.method == 'POST':
        form = GeocamMessageForm(request.POST)
        if form.is_valid():
            form.save()        
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