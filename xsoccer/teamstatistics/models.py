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

    FH_value = models.IntegerField("FH Value", default = 0, null=False)
    SH_value = models.IntegerField("SH Value", default = 0, null=False)
    ETFH_value = models.IntegerField("ETFH Value", null=True)
    ETSH_value = models.IntegerField("ETSH Value", null=True)
    FT_value = models.IntegerField("FT Value", default = 0, null=False)

    def __str__(self):
    	return "%s for %s in %s" % (self.statistic, self.team, self.game)
