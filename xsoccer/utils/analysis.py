# functions centered around analysis

# Sample commands to run:
"""

import utils.analysis as ua
p = ua.player("p164480")
t = ua.team("t1326")

p_games = ua.player_list_games(p)
t_games = ua.team_list_games(t)

stats = ua.player_game_stats(p, games[0])

ua.player_statistic_values(p,p_games[0],["passes_left", "accurate_pass", "aerial_won", "aerial_lost", "accurate_back_zone_pass", "accurate_fwd_zone_pass"])
ua.player_statistic_values(p,p_games[0],["passes_left"])

ua.team_statistic_values(t,t_games[0],["passes_left"])
ua.team_statistic_values(t,t_games[0])
"""
import time
import datetime 

from eventstatistics.models import EventStatistic
from games.models import Game
from lineups.models import Lineup
from players.models import Player
from playerstatistics.models import PlayerStatistic
from salaries.models import Salary
from statistictypes.models import StatisticType
from teams.models import Team
from teamstatistics.models import TeamStatistic
from venues.models import Venue


"""
PLAYER CENTRIC METHODS
"""
def player(player_uuid):
	"""Return a Player Django instance"""
	return Player.objects.get(uuid=player_uuid)

def player_list_games(player, start_date, end_date):
	"""Return a list of Game instances for a Player input, between a date range"""
	games = []

	for l in Lineup.objects.filter(player=player):
		if l.game.date >= start_date and l.game.date <= end_date:
			games.append(l.game)

	return games

def player_game_stats(player, game):
	"""Return all PlayerStatistics for a Player and Game"""
	stats = []

	for stat in PlayerStatistic.objects.filter(game=game).filter(player=player):
		stats.append(stat)

	return stats

def player_statistic_values(player, game, list_desired_stats = None):
	"""Return the PlayerStatistic value(s) (specified or not) for a player / game"""
	#Note: inputting a list of stats at once, as calling game_stats only once 
	#will save us dramatically in reducing hits to the database
	stats = player_game_stats(player, game)

	values = {}

	if list_desired_stats:
		for desired_stat in list_desired_stats:
			values[desired_stat] = 0.0

			for s in stats:
				if s.statistic.opta_statistic_type_name == desired_stat:
					values[desired_stat] = s.value
		return values
	else:
		for s in stats:
			values[s.statistic.opta_statistic_type_name] = s.value

		return values


"""
TEAM CENTRIC METHODS
"""
def team(team_uuid):
	"""Return a Team Django instance"""
	return Team.objects.get(uuid=team_uuid)

def team_list_games(team, start_date, end_date):
	"""Return a list of Game instances for a Team input, between two date ranges"""
	games = []

	for g in Game.objects.filter(home_team=team, date__range=[start_date,end_date]) \
				| Game.objects.filter(away_team=team, date__range=[start_date,end_date]):
		games.append(g)

	return games

def team_game_stats(team, game):
	"""Return all TeamStatistics for a Team and Game"""
	stats = []

	for stat in TeamStatistic.objects.filter(game=game).filter(team=team):
		stats.append(stat)

	return stats

def team_statistic_values(team, game, list_desired_stats=None):
	"""Return the TeamStatistic value(s) (specified or not) for a team / game"""
	#Note: inputting a list of stats at once, as calling game_stats only once 
	#will save us dramatically in reducing hits to the database
	stats = team_game_stats(team, game)

	values = {}

	if list_desired_stats:
		for desired_stat in list_desired_stats:
			values[desired_stat] = 0.0

			for s in stats:
				if s.statistic.opta_statistic_type_name == desired_stat:
					values[desired_stat] = s.value
		
		return values
	else:
		for s in stats:
			values[s.statistic.opta_statistic_type_name] = s.value

		return values

def team_wins(team):
	"""Return a list of Game instances where the Team won"""
	wins = []
	
	for g in Game.objects.filter(winner=team):
		wins.append(g)

	return wins

def team_losses(team, start_date=datetime.date(1900, 1, 1), end_date=datetime.date(2900, 1, 1)):
	"""Return a list of Game instances where a Team lost"""
	losses = []

	games = team_list_games(team, start_date, end_date)

	for g in games:
		if g.winner == None:
			continue
		elif g.winner == team:
			continue
		else:
			losses.append(g)

	return losses

def team_ties(team, start_date=datetime.date(1900, 1, 1), end_date=datetime.date(2900, 1, 1)):
	"""Return a list of Game instances where a Team tied"""
	ties = []

	games = team_list_games(team, start_date, end_date)

	for g in games:
		if g.winner == None:
			ties.append(g)

	return ties

def team_scoreless_ties(team, start_date=datetime.date(1900, 1, 1), end_date=datetime.date(2900, 1, 1)):
	"""Return a list of Game instances where a Team tied and nobody scored"""
	scoreless_ties = []

	games = team_list_games(team, start_date, end_date)

	for g in games:
		if g.winner == None and g.home_team_score == 0:
			scoreless_ties.append(g)

	return scoreless_ties

def team_game_result(team, game):
	"""Return the final result of the game as it relates to the team"""
	if game.winner == team:
		return "Win"
	elif game.winner and game.winner != team:
		return "Lose"
	elif game.home_team_score > 0:
		return "Tie"
	else:
		return "Scoreless Tie"
