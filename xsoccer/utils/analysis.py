# functions centered around analysis

# Sample commands to run:
"""

import utils.analysis as ua
p = ua.player("p164480")

games = ua.list_games(p)

stats = ua.game_stats(p, games[0])

"""

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