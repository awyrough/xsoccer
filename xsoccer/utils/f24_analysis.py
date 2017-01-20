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
from qualifiers.models import Qualifier
from games.models import Game
from lineups.models import Lineup
from players.models import Player
from playerstatistics.models import PlayerStatistic
from salaries.models import Salary
from statistictypes.models import StatisticType
from teams.models import Team
from teamstatistics.models import TeamStatistic
from venues.models import Venue


import utils.analysis as ua

"""
Passing Events  

type_id = 1 <- Pass

	qualifier id = 213 = angle of ball relative to direction of play (in radians; 0 to 6.28)
	qualifier id = 212 = estimated length of pass in meters
	qualifier id = 140 = pass-end-x pitch coord
	qualifier id = 141 = pass-end-y pitch coord

	qualifier id = 5 = freekick
	qualifier id = 6 = corner 
	qualifier id = 2 = cross / short corner (?)

type_id = 8 <- opponent intercepts ball (not a clearance)

"""

def is_type_id(instance, typeID):
	if instance.type_id == typeID:
		return instance
	else:
		return None

def is_qualifier_id(instance, qualifierID):
	if instance.qualifier_id == qualifierID:
		return instance
	else:
		return None

def pass_elements(event_stat):
	"""Pull pass elements out of an EventStatistic and it's associated Qualifiers"""
	if event_stat.type_id not in [1]:
		raise Exception("%s is not a passing event" % (event_stat))

	player = event_stat.player
	x_start = event_stat.x
	y_start = event_stat.y

	minute = event_stat.minute
	second = event_stat.second
	relative_seconds = event_stat.relative_seconds

	x_end = None
	y_end = None
	length = None
	angle = None

	for Q in Qualifier.objects.filter(event_statistic=event_stat):
		if is_qualifier_id(Q, 140):
			x_end = float(Q.value)
		elif is_qualifier_id(Q, 141):
			y_end = float(Q.value)
		elif is_qualifier_id(Q, 212):
			length = float(Q.value)
		elif is_qualifier_id(Q, 213):
			angle = float(Q.value)

	pass_tuple = (player, minute, second, relative_seconds, x_start, y_start, x_end, y_end, length, angle)

	return pass_tuple

def create_pass_chains(game, team):
	"""Method to iterate through a list of EventStatistics and identify passing chains for a given team"""
	event_stats = EventStatistic.objects.filter(game=game)

	pass_chains = []

	i = 0 
	chain = []
	skipped = 0

	for stat in event_stats:
		if is_type_id(stat,1) and stat.team == team:
			chain.append(stat)
		else:
			if len(chain):
				pass_chains.append(chain)
			chain = []
	if len(chain):
		pass_chains.append(chain)

	#print pass_chains

	for item in pass_chains:
		print ""
		for i in item:
			print i 


