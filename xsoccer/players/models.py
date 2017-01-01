from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Player(models.Model):
    """
    An Opta player. 

    Should be biographical and meta information about the player.
    """
    # Opta UUID (NB: Different than Django-generated pk/id) 
    uuid = models.CharField("Opta uID", max_length=255, unique=True)
    # Player First Name
    first_name = models.CharField("First Name", max_length=255)
	# Player Last Name
    last_name = models.CharField("Last Name", max_length=255)
   	# Player Birth Date
    birth_date = models.DateField("Birth Date", null=True, blank=True)
    # Player Birth Place
    birth_place = models.CharField("Birth Place", max_length=255, null=True, blank=True)
    # Player First Nationality
    nationality = models.CharField("Nationality", max_length=255, null=True, blank=True)
    # Player Weight
    weight = models.FloatField("Weight", default=0.0)
    # Player Height
    height = models.FloatField("Height", default=0.0)
    # Real Position
    position = models.CharField("Real Position", max_length=255, null=True, blank=True)
    # Real Position Side
    position_side = models.CharField("Real Position Side", max_length=255, null=True, blank=True)
    # Country
    country = models.CharField("Country", max_length=255, null=True, blank=True)
    
    def __str__(self):
		return "%s %s (uID = %s)" % (self.first_name, self.last_name, self.uuid)
