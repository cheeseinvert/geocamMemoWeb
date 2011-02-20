# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from geocamMemo.models import GeocamMessage
from geocamMemo.forms import GeocamMessageForm

@login_required
def message_list(request):
    
    messages = GeocamMessage.objects.all()
    return render_to_response('geocamMemo/messagelist.html', 
                              {"gc_msg": messages}, context_instance=RequestContext(request))

@login_required
def index(request):
    return render_to_response('geocamMemo/home.html',
                              {}, context_instance=RequestContext(request))

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