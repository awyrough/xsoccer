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
import math

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

	# for item in pass_chains:
	# 	print ""
	# 	for i in item:
	# 		print i 

	return pass_chains


def distance(coordinate_tuple):
	"""Intake a coordinate tuple, return the distance between points"""
	x1 = coordinate_tuple[0]
	y1 = coordinate_tuple[1]
	x2 = coordinate_tuple[2]
	y2 = coordinate_tuple[3]

	dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)

	return dist

def x_distance(coordinate_tuple):
	"""Intake a coordinate tuple, return the net x vector value"""
	x1 = coordinate_tuple[0]
	x2 = coordinate_tuple[2]

	return x2-x1

def y_distance(coordinate_tuple):
	"""Intake a coordinate tuple, return the net y vector value"""
	y1 = coordinate_tuple[1]
	y2 = coordinate_tuple[3]

	return y2-y1

def seconds_to_game_time(seconds,option):
	"""Intake aggregate seconds and convert to game minute / second"""
	if option == "string":
		return '{}\'{}\"'.format(*divmod(seconds, 60))
	elif option == "float":
		return float(seconds)/60
	else:
		raise Exception("%s is not an appropriate conversion option" % (option))

def pass_chain_diagnostics(pass_chain, ignore_singles=False):
	"""Method for handling a chain of passes and outputting descriptive information"""
	num_passes = len(pass_chain)

	if ignore_singles and num_passes == 1:
		return None
	#list of pass elements for the whole chain
	pass_chain_elements = []
	#list of player instances
	player_sequence = []
	#list of tuples for keeping track of 4x tuple coordinate information
	coordinates = []
	#total distance of ball movement
	total_distance = 0.0

	for item in pass_chain:
		#get pass_chain item's pass elements
		item_elements = pass_elements(item)
		#save those in a list
		pass_chain_elements.append(item_elements)
		#record the players involved
		player_sequence.append(item_elements[0])
		#record the coordinate movements
		x1y1x2y2 = (item_elements[4], item_elements[5], item_elements[6], item_elements[7])
		total_distance += distance(x1y1x2y2)
		coordinates.append(x1y1x2y2)

	start_xy = (pass_chain_elements[0][4], pass_chain_elements[0][5])
	end_xy = (pass_chain_elements[num_passes-1][6], pass_chain_elements[num_passes-1][7])

	#4x tuple for total x/y coordinates traveled
	net_coordinates = (start_xy[0], start_xy[1], end_xy[0], end_xy[1])

	#elapsed time in seconds
	elapsed_time = pass_chain_elements[num_passes-1][3]-pass_chain_elements[0][3]

	#game minute/second of start
	chain_start_seconds = int(pass_chain_elements[0][1])*60 + int(pass_chain_elements[0][2])

			#0 pass_chain_elements
			#1 player_sequence
			#2 net_coordinates
			#3 coordinates
			#4 distance(net_coordinates)
			#5 x_distance(net_coordinates)
			#6 total_distance
			#7 num_passes
			#8 chain_start_seconds
			#9 elapsed_time

	return [pass_chain_elements,player_sequence,net_coordinates,coordinates,distance(net_coordinates),x_distance(net_coordinates),total_distance,num_passes,chain_start_seconds,elapsed_time]


def tempo_from_pass_diagnostics(diagnostic):
	"""Method for handling a chain_pass diagnostic and outputting it's tempo

	Shouldn't be calculated for pass chains of 1 pass

	tempo = pass count / cumulative time
	"""
	pass_count = diagnostic[7]
	elapsed_time = diagnostic[9]

	if elapsed_time > 0:
		return float(pass_count) / elapsed_time
	else:
		return None

def total_velocity_from_pass_diagnostics(diagnostic):
	"""Method for handling a chain_pass diagnostic and outputting it's total velocity

	Shouldn't be calculated for pass chains of 1 pass

	total velocity = total distance / cumulative time
	"""
	total_distance = diagnostic[6]
	elapsed_time = diagnostic[9]
	pass_count = diagnostic[7]

	if pass_count > 1:
		return float(total_distance) / elapsed_time
	else:
		return None

def vertical_velocity_from_pass_diagnostics(diagnostic):
	"""Method for handling a chain_pass diagnostic and outputting it's vertical velocity

	Shouldn't be calculated for pass chains of 1 pass

	vertical velocity = vertical distance / cumulative time
	"""
	vertical_distance = diagnostic[5]
	elapsed_time = diagnostic[9]
	pass_count = diagnostic[7]

	if pass_count > 1:
		return float(vertical_distance) / elapsed_time
	else:
		return None