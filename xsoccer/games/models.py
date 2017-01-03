from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Game(models.Model):
    """
    An Opta game.
    """
    # Opta UUID (NB: Different than Django-generated pk/id) 
    uuid = models.CharField("Opta uID", max_length=255, unique=True)
    date = models.DateField("Date Played")
    
    attendance = models.IntegerField("Attendance", null=True, blank=True)
	venue = models.ForeignKey('venues.Venue', on_delete=models.PROTECT, null=False)
	
	home_team = models.ForeignKey('teams.Team', on_delete=models.PROTECT, null=False)
	away_team = models.ForeignKey('teams.Team', on_delete=models.PROTECT, null=False)

	winner = models.ForeignKey('teams.Team', on_delete=models.PROTECT, null=False)

	def __str__(self):
		return "%s at %s on %s (Winner = %s)" % (
			self.away_team, self.home_team, self.date, self.winner)

	def location(self):
		# The venue portion should always be populated for Opta games
		if self.venue:
			return self.venue
		else:
			return None

	class Meta:
		unique_together = ["home_team", "away_team", "date"]