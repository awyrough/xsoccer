# functions centered around analysis

# Sample commands to run:
"""

import utils.analysis as ua
p = ua.player("p164480")

games = ua.list_games(p)

stats = ua.game_stats(p, games[0])

ua.statistic_values(p,games[0],["passes_left", "accurate_pass", "aerial_won", "aerial_lost", "accurate_back_zone_pass", "accurate_fwd_zone_pass"])
ua.statistic_values(p,games[0],["passes_left"])

"""
import time

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


def list_games(player):
	"""Return a list of Game instances for a Player input"""
	games = []

	for l in Lineup.objects.filter(player=player):
		games.append(l.game)

	return games

def player(player_uuid):
	"""Return a Player Django instance"""
	return Player.objects.get(uuid=player_uuid)

def game_stats(player, game):
	"""Return all PlayerStatistics for a Player and Game"""
	stats = []

	for stat in PlayerStatistic.objects.filter(game=game).filter(player=player):
		stats.append(stat)

	return stats

def statistic_values(player, game, list_desired_stats):
	"""Return the value(s) of the specific statistic(s) for a player / game"""
	#Note: inputting a list of stats at once, as calling game_stats only once 
	#will save us dramatically in reducing hits to the database
	stats = game_stats(player, game)

	values = {}

	for desired_stat in list_desired_stats:
		values[desired_stat] = 0.0

		for s in stats:
			if s.statistic.opta_statistic_type_name == desired_stat:
				values[desired_stat] = s.value
	
	return values