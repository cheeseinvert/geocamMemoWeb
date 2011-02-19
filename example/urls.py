# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin 
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/logout/$', 'geocamMemo.views.logout_view'),
    url(r'^accounts/login/$', 'geocamMemo.views.login_view'),
    url(r'^$', 'geocamMemo.views.message_list'),
    url(r'^messages/index',  'geocamMemo.views.message_list'),  #include('geocamMemo.urls')),
)

urlpatterns = urlpatterns + patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    ) if settings.DEBUG else urlpatterns

