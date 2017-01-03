from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Team(models.Model):
    """
    An Opta team. 

    Should be biographical and meta information about the team.
    """
    # Team Name
    name = models.CharField(max_length=255)
    # Opta UUID (NB: Different than Django-generated pk/id) 
    uuid = models.CharField(max_length=255, unique=True)

    def __str__(self):
		return self.name
