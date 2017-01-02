from __future__ import unicode_literals

from django.db import models


class Player(models.Model):
    """
    An Opta player. 

    Should be biographical and meta information about the player.
    """
    # Opta UUID (NB: Different than Django-generated pk/id) 
    uuid = models.CharField(max_length=255, unique=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    birth_date = models.DateField(null=True)
    birth_place = models.CharField(max_length=255, null=True)
    nationality = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)

    weight = models.FloatField(default=0.0, null=True)
    height = models.FloatField(default=0.0, null=True)

    # TODO(aj): Determine if position and position_side should be abstracted
    # to allow for a CHOICE field and not allow arbitrary values here
    # i.e. RIGHT, LEFT, CENTER...DEFENDER, MIDFIELDER, GK
    position = models.CharField(max_length=255, null=True)
    position_side = models.CharField(max_length=255, null=True)

    def __str__(self):
		return "%s %s (uID = %s)" % (self.first_name, 
                                             self.last_name, 
                                             self.uuid)
