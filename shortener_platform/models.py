from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from shortener_platform.utils import generate_unique_url_identifier


class Link(models.Model):
    url = models.URLField()
    alt_url = models.CharField(max_length=10, auto_created=True, unique=True, default=generate_unique_url_identifier)
    owner = models.ForeignKey(User, related_name='user_links', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    expires_at = models.DateTimeField(blank=True, null=True)
    update_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

