# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django import forms

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
            # Return an 'invalid login' error message.
            return render_to_response('example/login.html',
                                {'form':LoginForm()},
                                context_instance=RequestContext(request))
    else:
        return render_to_response('example/login.html',
                                {'form':LoginForm()},
                                context_instance=RequestContext(request))
        
class LoginForm(forms.Form):
    username = forms.CharField(label=(u'Username'))
    password = forms.CharField(label=(u'Password'),widget=forms.PasswordInput(render_value=False))