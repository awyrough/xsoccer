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
	venue = models.ForeignKey('venues.Venue', on_delete=models.PROTECT, related_name="game_venue")
	home_team = models.ForeignKey('teams.Team', on_delete=models.PROTECT, related_name="game_home_team")
	away_team = models.ForeignKey('teams.Team', on_delete=models.PROTECT, related_name="game_away_team")
	winner = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name="game_winner")
	first_half_time = models.IntegerField("1st Half Length (mins)")
	second_half_time = models.IntegerField("2nd Half Length (mins)")
	home_team_score = models.IntegerField("Final Score of Home Team", null=True)
	away_team_score = models.IntegerField("Final Score of Away Team", null=True)

	def __str__(self):
		return "%s at %s on %s (%s)" % (
			self.away_team, self.home_team, self.date, self.uuid)
		# return "%s at %s on %s (W = %s)" % (
		# 	self.away_team, self.home_team, self.date, self.winner)

	def location(self):
		# The venue portion should always be populated for Opta games
		if self.venue:
			return self.venue
		else:
			return None

	def game_length(self):
		return self.first_half_time + self.second_half_time

	def atmosphere(self):
		return (float(self.attendance) / float(self.venue.capacity)) * 100

	def team_score(team_uuid):
		if team_uuid == home_team.uuid:
			return home_team_score
		elif team_uuid == away_team.uuid:
			return away_team_score
		else:
			return "Your logic is wrong"

	#give us the ability to manually update the DB instances at any point! (added to Game model to update scores)
	def update(self, **kwargs):
			if self._state.adding:
				raise self.DoesNotExist
			for field, value in kwargs.items():
				setattr(self, field, value)
			self.save(update_fields=kwargs.keys())

	class Meta:
		unique_together = ["home_team", "away_team", "date"]
