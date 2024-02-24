from django.db import models

from avanan.models import BaseModel


class DLPPattern(BaseModel):
    name = models.CharField(max_length=100)
    pattern = models.CharField(max_length=255)
