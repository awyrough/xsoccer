# functions centered around f24 analysis

import time
import datetime 
import math
import os
import csv
from collections import Counter

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

def is_type_id_many(instance, typeIDlist):
	instance_type = instance.type_id

	for typeID in typeIDlist:
		if instance_type == typeID:
			return instance

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

	player_position = Lineup.objects.get(game=event_stat.game, player=player).player_formation_number

	pass_tuple = (player, minute, second, relative_seconds, x_start, y_start, x_end, y_end, length, angle, player_position)

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

	"""if ignore_singles=True, this means we want to ignore single-pass pass chains"""
	num_passes = len(pass_chain)

	if ignore_singles and num_passes == 1:
		return None
	#list of pass elements for the whole chain
	pass_chain_elements = []
	#list of player instances
	player_sequence = []
	#list of player positions
	position_sequence = []
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
		position_sequence.append(item_elements[10])
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
			#10 player position sequence

	return [pass_chain_elements,player_sequence,net_coordinates,coordinates,distance(net_coordinates),x_distance(net_coordinates),total_distance,num_passes,chain_start_seconds,elapsed_time,position_sequence]


def game_diagnostics(game, team, ignore_singles=False):
	"""Input a game, team and note if you want to ignore single-passes..
	
	will pull all pass chain diagnostics in that game and return a list of lists"""

	#diagnostic legend, as an FYI:
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
		#10 player position sequence


	#get passing chains
	pass_chains = create_pass_chains(game, team)

	#pull statistics on passing chains
	game_diagnostics = []
	for chain in pass_chains:
		pass_chain_diagnostic_results = pass_chain_diagnostics(chain, ignore_singles=True)
		
		#ignore sequences that are unrealistically short, as this is a data collection error
		if pass_chain_diagnostic_results and pass_chain_diagnostic_results[9] >= 0.1:
			game_diagnostics.append(pass_chain_diagnostic_results)

	return game_diagnostics

def unique_players_involved(player_list):
	"""Return a list of distinct players involved in passing chain"""
	unique = []
	for player in player_list:
		if player not in unique:
			unique.append(player)

	#sort the list by player uuid, so if the same combination of players always looks the same
	unique_sorted = sorted(unique, key=lambda x: x.uuid)
	return unique_sorted

def frequency_of_lists(list_of_lists):
	"""Return the frequency of lists appearing in a list of lists"""
	c = Counter(tuple(x) for x in iter(list_of_lists))

	return c.most_common()

def frequency_of_items(list):
	"""Return the frequency of items appearing in a list"""
	c = Counter(list)

	return c.most_common()

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

def to_csv_single_gameteam_stats(game_diagnostics, team, game):
	"""
	To be run when we want to save to csv a single team's pass statistics over the course of a game
	"""
	os.chdir("/Users/Swoboda/Desktop/analysis2/")
	team_uuid = team.uuid
	game_uuid = game.uuid
	game_date = game.date

	output_filename = "analysis2" + "_" + game_uuid + "_" + team_uuid + ".csv"

	#create header row
	header = []
	header += ["Date"]
	header += ["Game"]
	header += ["Team"]
	header += ["Game_Minutes"]
	header += ["Pass_Count"]
	header += ["Elapsed_Time"]
	header += ["Tempo"]
	header += ["Total_Velocity"]
	header += ["Vertical_Velocity"]

	output = open(output_filename, "a")
	writer = csv.writer(output, lineterminator="\n")

	writer.writerow(header)

	#Diagnostic legend:
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
	for diagnostics in game_diagnostics:
		r = []
		r += [game_date]
		r += [game_uuid]
		r += [team_uuid]
		r += [seconds_to_game_time(diagnostics[8],"float")]
		r += [diagnostics[7]]
		r += [diagnostics[9]]
		r += [tempo_from_pass_diagnostics(diagnostics)]
		r += [total_velocity_from_pass_diagnostics(diagnostics)]
		r += [vertical_velocity_from_pass_diagnostics(diagnostics)]

		if len(header) != len(r):
			raise Exception("Rows you're about to print are not same dimension as header. Check this!")
		writer.writerow(r)

	output.close()



def to_csv_histogram(histogram_lists,team,title=""):
	"""
	To be run when we want to save to csv a list of frequencies
	"""
	os.chdir("/Users/Swoboda/Desktop/analysis3/")
	team_uuid = team.uuid
	output_filename = "analysis3" + "_" + str(team_uuid) + "_" + title + ".csv"
	#create header row
	header = []
	header += ["Item"]
	header += ["Frequency"]

	output = open(output_filename, "a")
	writer = csv.writer(output, lineterminator="\n")

	writer.writerow(header)
	len_header = len(header)

	for h in histogram_lists:
		r = []
		r += [h[0]]
		r += [h[1]]

		if len_header != len(r):
			raise Exception("Rows you're about to print are not same dimension as header. Check this!")
		writer.writerow(r)

	output.close()


"""
Shot Events  

type_id = 13 <- Miss (off target; wide or over goal)

type_id = 14 <- Post

type_id = 15 <- Attempt Saved
	qualifier id = 82 <- blocked shot

type_id = 16 <- Goal

type_id = 60 <- Chance missed (..maybe include later?)

"""

def identify_shots(game, team):
	"""Method to iterate through a list of EventStatistics and identify shots for a given team"""
	event_stats = EventStatistic.objects.filter(game=game)

	shots = []

	for stat in event_stats:
		if is_type_id_many(stat,[13,14,15,16]) and stat.team == team:
			shots.append(stat)

	return shots

def is_inside_box(event):
	"""Method to determine if an event takes place inside the box"""

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

	player_position = Lineup.objects.get(game=event_stat.game, player=player).player_formation_number

	pass_tuple = (player, minute, second, relative_seconds, x_start, y_start, x_end, y_end, length, angle, player_position)

	return pass_tuple