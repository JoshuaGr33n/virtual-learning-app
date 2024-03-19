from django.db import models

from django.db import models
from django.conf import settings

class FriendRequest(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friend_requests_sent", on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friend_requests_received", on_delete=models.CASCADE)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('sender', 'receiver')  # Prevent duplicate requests

