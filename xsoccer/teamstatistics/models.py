from __future__ import unicode_literals

from django.db import models


# Create your models here.
class TeamStatistic(models.Model):
    """
    Opta F9 Team-level aggregate statistics. 
    """

    game = models.ForeignKey('games.Game', on_delete=models.CASCADE, related_name="game_for_teamstats")
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name="team_for_teamstats")
    statistic = models.ForeignKey('statistictypes.StatisticType', on_delete=models.CASCADE, related_name="stat_for_teamstats")

    first_half_value = models.IntegerField("1H Value", default = 0, null=False)
    second_half_value = models.IntegerField("2H Value", default = 0, null=False)
    extra_time_first_half_value = models.IntegerField("ET1H Value", null=True)
    extra_time_second_half_value = models.IntegerField("ET2H Value", null=True)
    full_time_value = models.IntegerField("FT Value", default = 0, null=False)

    def __str__(self):
    	return "%s for %s in %s" % (self.statistic, self.team, self.game)
