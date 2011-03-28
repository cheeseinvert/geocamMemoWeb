from django.core.management.base import BaseCommand, CommandError
from geocamMemo.models import MemoMessage
from django.contrib.auth.models import User
from datetime import datetime
import random

class Command(BaseCommand):
    args = '<usrname(optional)> msgText'
    help = 'Generates a random memo message'

    def handle(self, *args, **options):
        username = None
        if(len(args)):
            username = args[0]    
            
        try:
            user = User.objects.get(username = username)
            args = args[1:]
        except:
            users = User.objects.all()
            user = users[random.randrange(0,len(users)-1)]
        
        messageContent = " ".join(args)
        
        if(len(args) > 0):
            messageContent
        else:
            messageContent = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec elit erat, porttitor sed tempor id, eleifend et diam. Mauris quam libero, tristique non fringilla nec, suscipit ac mauris. Curabitur sed lacus et ipsum vestibulum suscipit sed a neque. Nullam sed ipsum vitae nisi imperdiet egestas nec a nisi. Mauris pulvinar massa in felis dapibus tempus. Donec in nulla tellus, vel venenatis augue. Duis nisi tellus, vehicula at egestas et, laoreet vitae quam. Ut ullamcorper fermentum facilisis. Sed dapibus odio a mi congue interdum dapibus urna placerat. Vestibulum faucibus metus sed justo convallis mollis. Mauris lorem mauris, blandit eget faucibus nec, feugiat non risus.".split()
            random.shuffle(messageContent)
            messageContent = " ".join(messageContent[0:random.randrange(10, 30)])
        
        contenttimestamp = datetime.now()
        msg = MemoMessage()
        msg.content_timestamp = contenttimestamp
        msg.content = messageContent
        msg.author = user
        
        cmusvlat = 37.41029;
        cmusvlon = -122.05944;
        
        msg.latitude = cmusvlat + (random.random()-0.5)*0.02
        msg.longitude = cmusvlon + (random.random()-0.5)*0.02
        msg.accuracy = random.randrange(0,120)       
        
        msg.save()
        
        print msg
        