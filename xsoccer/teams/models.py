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
		return "%s (%s)" % (self.name, self.uuid)

    #give us the ability to manuall update the DB instances at any point! (mostly for things like venues / teams)
    def update(self, **kwargs):
            if self._state.adding:
                raise self.DoesNotExist
            for field, value in kwargs.items():
                setattr(self, field, value)
            self.save(update_fields=kwargs.keys())