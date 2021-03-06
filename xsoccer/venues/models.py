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
    country = models.CharField(max_length=255,null=True)
    # TODO(hill): I think we should include capacity and surface-type as well; 
    # we can probably just load those in manually using a csv file? 

    capacity = models.IntegerField(default=0,null=True)
    surface = models.CharField(max_length=100,default="Unknown",null=True)

    def __str__(self):
        return "%s (%s)" % (self.name, self.uuid)

    #give us the ability to manuall update the DB instances at any point! (mostly for things like venues / teams)
    def update(self, **kwargs):
            if self._state.adding:
                raise self.DoesNotExist
            for field, value in kwargs.items():
                setattr(self, field, value)
            self.save(update_fields=kwargs.keys())