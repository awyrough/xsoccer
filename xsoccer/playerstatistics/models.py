from __future__ import unicode_literals

from django.db import models

# Create your models here.
class PlayerStatistic(models.Model):
    """
    Opta F9 player-level aggregate statistics. 
    """

    game = models.ForeignKey('games.Game', on_delete=models.CASCADE, related_name="game_for_playerstats")
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name="player_for_playerstats")
    statistic = models.ForeignKey('statistictypes.StatisticType', on_delete=models.CASCADE, related_name="stat_for_playerstats")

    value = models.IntegerField("statistic_value", default = 0, null=False)

    def __str__(self):
    	return "%s for %s in %s" % (self.statistic, self.game, self.game)
