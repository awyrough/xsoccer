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

    FH_value = models.FloatField("FH Value", default = 0.0, null=True)
    SH_value = models.FloatField("SH Value", default = 0.0, null=True)
    ETFH_value = models.FloatField("ETFH Value", null=True)
    ETSH_value = models.FloatField("ETSH Value", null=True)
    value = models.FloatField("Value", default = 0.0, null=False)

    def __str__(self):
    	return "%s for %s in %s" % (self.statistic, self.team, self.game)

    class Meta:
        unique_together = (("game", "team", "statistic"),)