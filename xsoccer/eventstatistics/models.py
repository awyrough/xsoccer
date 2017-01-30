from __future__ import unicode_literals

from django.db import models

# Create your models here.
class EventStatistic(models.Model):
    """
    Opta F24 events. View Opta documentation and appendix for further info on data logic
    """

    ZERO_OR_ONE = (
    	(0, 0),
    	(1, 1),
    	)

    uuid = models.BigIntegerField("Opta Unique ID", unique=True, null=False)

    event_id = models.IntegerField("Unique ID within a game", null=False)
    
    game = models.ForeignKey('games.Game', on_delete=models.CASCADE, related_name="game_of_event")
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name="player_of_event", null=True)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name="team_of_event")

    type_id = models.IntegerField("type of event", null=False)
    
    #1 = first half; 2 = second half; 3 = first half ET; 4 = second half EF; 5 = PKs; etc.
    period_id = models.IntegerField(null=False)

    minute = models.IntegerField("Game time minute", null=False)
    second = models.IntegerField("Game time second", null=False)
    
    outcome = models.IntegerField(null=False, choices=ZERO_OR_ONE)

    assist = models.BooleanField(null=False, default=False)
    keypass = models.BooleanField(null=False, default=False)

    # This is the length of the pitch where 0 is always the defensive goal line 
    # and 100 is the attacking goal line. This is true for both teams in both halves.
    # All coordinates are always displayed as if both teams are playing left to right.
    x = models.FloatField(null=False)
    # This is the width of the pitch where the right hand touch line (nearest the TV 
    # camera) is 0 and the left hand touch line (furthest away) is 100. 
    y = models.FloatField(null=False)

    #time of event in seconds, relative to scheduled game start
    relative_seconds = models.FloatField("Relative Seconds of Event", null=False, default=-999999)

    def __str__(self):
    	return "%s'%s\" - type_id=%s; %s" % (self.minute, self.second, self.type_id, self.team)

    def game_minute(self):
    	return round(self.minute + float(self.second)/60)

    class Meta:
    #we technically shouldn't need to add type_id to this, but it fails without it (see event_id="777" in f791390)
    #not sure if this unique constraint is worth anything...
        unique_together = (("game", "team", "event_id","type_id"),)
        ordering = ["period_id","minute", "second", "relative_seconds"]