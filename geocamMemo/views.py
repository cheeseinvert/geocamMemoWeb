# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
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
    return render_to_response('messagelist.html', 
                              {"gc_msg": messages}, context_instance=RequestContext(request))

@login_required
def message_list_filtered_username(request, username):
    user = get_object_or_404(User, username=username)
    
    messages = GeocamMessage.objects.filter(author = user.pk).order_by('-content_timestamp')
    return render_to_response('messagelist.html', 
                              {"gc_msg": messages,
                               "userstring": get_user_string(user)}, context_instance=RequestContext(request))

def index(request):
    return render_to_response('home.html',
                              {}, context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page
                return HttpResponseRedirect('/')
            else:
                # Return a 'disabled account' error message
                pass
        else:
            # Return an 'invalid login' error message.
            pass
    else:
        return render_to_response('login.html',
                                {'form':LoginForm()},
                                context_instance=RequestContext(request))
@login_required
def create_message(request):
    if request.method == 'POST':
        form = GeocamMessageForm(request.POST)
        if form.is_valid():
            form.save()        
            return HttpResponseRedirect('/memo/messages/')
        else:
            return render_to_response('message_form.html',
                                  {'form':form},
                                  context_instance=RequestContext(request))
    else:
        form = GeocamMessageForm()
        return render_to_response('message_form.html',
                                  {'form':form },                                   
                                  context_instance=RequestContext(request))
    
       
class LoginForm(forms.Form):
    username = forms.CharField(label=(u'Username'))
    password = forms.CharField(label=(u'Password'),widget=forms.PasswordInput(render_value=False))