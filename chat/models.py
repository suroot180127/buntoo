from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
import datetime

from django.core.cache import cache
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    
    def last_seen(self):
        return cache.get('last_seen_%s' % self.user.username)
    
    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > (self.last_seen() + datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)):
                return False
            else:
                return True
        else: 
            return False




class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    message = models.CharField(max_length=1200)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    def notify_ws_clients(self):
        """
        Inform client there is a new message.
        """
        notification = {
            'type': 'recieve_group_message',
            'message': '{}'.format(self.message),
            'receiver': '{}'.format(self.receiver.username)
        }

        channel_layer = get_channel_layer()
        print("user.id {}".format(self.sender.id))
        print("user.id {}".format(self.receiver.id))

        async_to_sync(channel_layer.group_send)("{}".format(self.sender.id), notification)
        async_to_sync(channel_layer.group_send)("{}".format(self.receiver.id), notification)

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.id
        self.message = self.message.strip()  # Trimming whitespaces from the bodyW
        super(Message, self).save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()

    class Meta:
        ordering = ('timestamp',)


