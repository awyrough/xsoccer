from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Venue(models.Model):
    """
    Generic venues (i.e. stadiums).
    """
    uuid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    # TODO(hillwyrough): We should make this a CHOICES field so we have
    # a distinct set of countries to choose from.
    country = models.CharField(max_length=255)
    # TODO(hill): I think we should include capacity and surface-type as well; 
    # we can probably just load those in manually using a csv file? 

    #capacity = models.IntegerField(default=0,null=True)
    #surface = models.CharField(...)

    def __str__(self):
        return self.name