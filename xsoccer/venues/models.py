from __future__ import unicode_literals

from django.db import models


class Venue(models.Model):
    """
    Generic venues (i.e. stadiums).
    """
    uuid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    # TODO(hillwyrough): We should make this a CHOICES field so we have
    # a distinct set of countries to choose from.
    country = models.CharField(max_length=255)
