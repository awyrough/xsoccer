from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Lineup(models.Model):
    """
    Lineups of a team in a game; from Opta F9 dataset. 
    """
    POSITIONS = (
        ("Goalkeeper", "Goalkeeper"),
        ("Wing Back", "Wing Back"),
        ("Full Back", "Full Back"),
        ("Defender","Defender"),
        ("Central Defender", "Central Defender"),
        ("Defensive Midfielder","Defensive Midfielder"),
        ("Attacking Midfielder","Attacking Midfielder"),
        ("Central Midfielder","Central Midfielder"),
        ("Midfielder","Midfielder"),
        ("Winger","Winger"),
        ("Striker","Striker"),
        ("Second Striker","Second Striker"),
        ("Substitute","Substitute")
        )

    LINEUP_NUMBERS = (
    	(0,0),
    	(1,1),
    	(2,2),
    	(3,3),
    	(4,4),
    	(5,5),
    	(6,6),
    	(7,7),
    	(8,8),
    	(9,9),
    	(10,10),
    	(11,11),
    	)

    game = models.ForeignKey('games.Game', on_delete=models.CASCADE, related_name="game_for_lineup")
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name="team_for_lineup")
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name="player_for_lineup")
    
    team_formation = models.CharField(max_length=25, null=False)
    #player's game-start position
    player_position = models.CharField(max_length=255, choices=POSITIONS, null=False)
    #player's position if they end up getting subbed
    player_subposition = models.CharField(max_length=255, null=True)

    is_captain = models.BooleanField(default=False)
    player_formation_number = models.IntegerField(default=0,choices=LINEUP_NUMBERS)

    def __str__(self):
    	if self.is_captain:
    		return "%s [C] - %s (Pos.%s) in a %s for %s in %s" % (self.player
    							,self.player_position
    							,self.player_formation_number
    							,self.team_formation
                                ,self.team
                                ,self.game)
    	else:
    		return "%s - %s (Pos.%s) in a %s for %s in  %s" % (self.player
    							,self.player_position
    							,self.player_formation_number
    							,self.team_formation
                                ,self.team
                                ,self.game)

    class Meta:
        unique_together = (("game", "player"),)