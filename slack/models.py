from django.db import models
from avanan.models import BaseModel
from dlp.models import DLPPattern


class FlaggedMessage(BaseModel):
    TYPE_CHOICES = [
        ('MSG', 'Message'),
        ('FILE', 'File'),
    ]
    client_msg_id = models.CharField(max_length=255, unique=True)
    ts = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    text = models.TextField()
    user = models.CharField(max_length=100)
    team = models.CharField(max_length=100)
    channel = models.CharField(max_length=100)
    pattern = models.ForeignKey(DLPPattern, on_delete=models.SET_NULL, null=True, blank=True)
