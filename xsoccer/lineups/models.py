from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Lineup(models.Model):
    """
    Lineups of a team in a game; from Opta F9 dataset. 
    """

    game = models.ForeignKey('games.Game', on_delete=models.CASCADE, related_name="game_for_lineup")
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name="team_for_lineup")
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name="player_for_lineup")
    
    team_formation = models.CharField(max_length=25, null=False)
    #player's game-start position
    player_position = models.CharField(max_length=255, null=False)
    #player's position if they end up getting subbed
    player_subposition = models.CharField(max_length=255, null=True)

    is_captain = models.BooleanField(default=False)
    player_formation_number = models.IntegerField(default=0)

    def __str__(self):
    	if self.is_captain:
    		return "%s [C] (%s) playing as a %s in a %s" % (self.player
    							,self.player_position
    							,self.player_formation_number
    							,self.team_formation)
    	else:
    		return "%s (%s) playing as a %s in a %s" % (self.player
    							,self.player_position
    							,self.player_formation_number
    							,self.team_formation)

    class Meta:
        unique_together = (("game", "player"),)