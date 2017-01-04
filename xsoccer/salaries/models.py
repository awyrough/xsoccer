from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Salary(models.Model):
    """
    An Opta player salary. 
    """
    #this FK has a cascade on_delete setting, as without player info, this data is useless
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, null=False, related_name="player_tied_to_salary")

    season = models.IntegerField("Season", null=False)
    
    base_salary = models.FloatField("Base Salary ($)", default=0.0, null=True)
    compensation = models.FloatField("Total Compensation ($)", default=0.0, null=True)

    def __str__(self):
        return "%s ($%s;$%s in %s)" % (self.player, self.base_salary, self.compensation, self.season)
