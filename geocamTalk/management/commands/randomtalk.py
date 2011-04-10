from django.core.management.base import BaseCommand, CommandError
from geocamTalk.models import TalkMessage
from django.contrib.auth.models import User
from datetime import datetime
import random

class Command(BaseCommand):
    args = '<author username:optional> <recipient usernames(comma sep, no spaces):optional> text'
    help = 'Generates a random talk message'

    def handle(self, *args, **options):
        username = None
        if(len(args)):
            username = args[0]
            
        user = None
        recipients = []
        unames = None
        try:
            user = User.objects.get(username = username)
            args = args[1:]
            if(len(args)):
                unames = args[1].split(",");
                for uname in unames:
                    recipients.push(User.objects.get(username=uname))                
        except:
            users = User.objects.all()
            user = users[random.randrange(0,len(users)-1)]
            
        if(not unames):
            recipients = list(User.objects.all())
            random.shuffle(recipients)
            recipients = recipients[0:random.randrange(0,len(recipients)-1)]
            
        messageContent = " ".join(args)
        
        if(len(args) > 0):
            messageContent
        else:
            messageContent = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec elit erat, porttitor sed tempor id, eleifend et diam. Mauris quam libero, tristique non fringilla nec, suscipit ac mauris. Curabitur sed lacus et ipsum vestibulum suscipit sed a neque. Nullam sed ipsum vitae nisi imperdiet egestas nec a nisi. Mauris pulvinar massa in felis dapibus tempus. Donec in nulla tellus, vel venenatis augue. Duis nisi tellus, vehicula at egestas et, laoreet vitae quam. Ut ullamcorper fermentum facilisis. Sed dapibus odio a mi congue interdum dapibus urna placerat. Vestibulum faucibus metus sed justo convallis mollis. Mauris lorem mauris, blandit eget faucibus nec, feugiat non risus.".split()
            random.shuffle(messageContent)
            messageContent = " ".join(messageContent[0:random.randrange(10, 30)])
        
        contenttimestamp = datetime.now()
        msg = TalkMessage()
        msg.content_timestamp = contenttimestamp
        msg.content = messageContent
        msg.author = user
        cmusvlat = 37.41029;
        cmusvlon = -122.05944;
        
        msg.latitude = cmusvlat + (random.random()-0.5)*0.02
        msg.longitude = cmusvlon + (random.random()-0.5)*0.02
        msg.accuracy = random.randrange(0,120)       
        
        msg.save()

        msg.recipients = recipients
        
        msg.push_to_phone()
        
        print msg
        