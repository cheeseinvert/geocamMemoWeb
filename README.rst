===============
GeoCam Memo Web
===============

.. sectnum::

.. contents:: Contents

About
-----

The GeoCam Project helps people better understand and respond to disasters.
GeoCam consists of a GPS-enabled camera (or cell phone) and a web app for
sharing geotagged photos and other geospatial data.

GeoCam Memo is a scribing and note-taking application intended for use by search team members as they canvas the scene of a disaster. Notes can be recorded using text or audio and various forms of attachments (including but not limited to images) can be attached for transmission to a central server. All messages can be geotagged and categorized before saving to provide proper context when analyzing them via a web interface at a later time.

GeoCam Talk is a communication application intended to aid in communication during a search mission. Members can send text and audio messages to any subset of their team members while on the field from their mobile devices. All messages are sent through a central server which catalogs them for later analysis. Just as in Memo, all messages are geotagged to provide instant awareness of team member location.

This is the web application for both GeoCam Memo and GeoCam Talk

News
----

Visit http://sites.google.com/site/geocampracticum2011/ and http://disastercam.blogspot.com/ for updates.

Setup
-----
The GeoCam Memo and Talk applications were built using the Django framework and run on top of Python.

Dependencies
~~~~~~~~~~~~
  * Python 2.4 or higher (http://www.python.org/download/)
  * Django 1.2.5 or greater (http://www.djangoproject.com/)

1. Once all dependencies have been installed, clone the GeoCamMemoWeb repository to the path of your choice::

      git clone git@github.com:cheeseinvert/geocamMemoWeb.git

2. CD into your ./geocamMemoWeb/example path and run syncdb, creating an admin user if prompted::
      
      python manage.py syncdb
      
Running
-------
To run a development server, navigate to your ./geocamMemoWeb/example path and execute runserver::
      
      python manage.py runserver 0.0.0.0:8000
      
Pleast note that this must be done before the geocamTalkForAndroid and geocamTalkForMemo can be successfully run on your mobile device.

Testing
-------
Testing can be initiated from your ./geocamMemoWeb/example path using the test command::
      
      python manage.py test geocamMemo geocamTalk

See the Django documentation for more information on using manage.py

| __BEGIN_LICENSE__
| Copyright (C) 2008-2010 United States Government as represented by
| the Administrator of the National Aeronautics and Space Administration.
| All Rights Reserved.
| __END_LICENSE__