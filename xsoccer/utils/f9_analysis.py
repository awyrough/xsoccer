# functions centered around f9 file analysis

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

"""Explicitly Written"""
def player_stat(player, game, statistic):
	"""Simply return the QuerySet tied to a player, game, and statistic
	Value of creating this more manual step is so that we check if there 
	is more than one QuerySet returning
	"""
	player_stat = PlayerStatistic.objects.filter(game=game, player=player, statistic=statistic)

	if len(player_stat) > 1:
		print player_stat
		raise Exception("This should not return multiple values: %s" % (player_stat))

	return player_stat

def player_stat_value_per90(player, game, statistic):
	"""For a given player and game, return the KPI of interest on a per-90 minute basis"""
	p_stat = player_stat(player, game, statistic)
	p_stat_value = None

	if len(p_stat) == 0: #if no metric for this game, return nothing
		p_stat_value = 0 
	else:
		p_stat_value = p_stat[0].value

	time_played = player_stat(player, game, "mins_played")

	returned_value = None

	#if player didn't play in the game despite being in lineup
	if len(time_played) == 0:
		returned_value = None
	#if player is marked as playing 0 minutes this game, return nothing
	elif time_played[0].value == 0: 
		raise Exception("Player marked as playing in F9 file, but mins_played = 0. Should this happen?")
		if p_stat_value != 0:
			print "Shouldn't have non-zero value if player didn't play in game. %s mins; %s; %s value" % (time_played[0].value, p_stat, p_stat_value)
			raise Exception("")
		returned_value = None
	# COMMENTED BELOW OUT AS IT IS UNNECESSARY WITH THE ELSE STATEMENT
	# elif time_played[0].value > 0 and p_stat_value == 0:
	# 	returned_value = 0
	else:
		returned_value = float(p_stat_value) / (time_played[0].value / 90.0)

	return returned_value

def game_list_player_stat_values(player, game_list, statistic):
	"""For a set of games and a given player, return the KPI's of interest"""
	values = []
	for game in game_list:
		v = player_stat_value_per90(player, game, statistic)
		if v >= 0: #ignore None values
			values.append(v)

	return values

def timeframe_player_stat_list_values(player, start_date, end_date, stat_list):
	"""For a timeframe between start/end dates, return dictionary of KPI values of interest"""
	game_list = ua.player_list_games(player, start_date, end_date)
	values = {}

	for stat in stat_list:
		values[stat] = game_list_player_stat_values(player, game_list, stat)

	return values

def timeframe_player_list_stat_list_values(player_list, start_date, end_date, stat_list):
	"""For a LIST OF PLAYERS, in a given timeframe between start/end dates, 
	return dictionary of KPI values of interest"""

	game_dict = {}
	for player in player_list:
		game_dict[player] = ua.player_list_games(player, start_date, end_date)

	kpikey_values = {}

	for stat in stat_list:
		kpikey_values[stat] = {}

		for player in player_list:
			kpikey_values[stat][player] = game_list_player_stat_values(player, game_dict[player], stat)

	return kpikey_values




"""Leftover from f24_analysis"""
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
	if not is_type_id(event_stat, 1):
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


def game_diagnostics(game, team, ignore_singles=True):
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
		pass_chain_diagnostic_results = pass_chain_diagnostics(chain, ignore_singles=ignore_singles)
		
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
		#10 player position sequence
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

def to_csv_timeperiod_team_passing_stats(team, game_list, textstring):
	"""
	To be run when we want to save to csv a single team's pass statistics over the course of a set of games
	
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
		#10 player position sequence
	"""
	os.chdir("/Users/Swoboda/Desktop/analysis2redo/")
	team_uuid = team.uuid
	output_filename = "analysis2redo" + "_" + team_uuid + textstring + ".csv"

	#create header row
	header = []
	header += ["Date"]
	header += ["Game ID"]
	header += ["Game"]
	header += ["Team ID"]
	header += ["Team"]
	header += ["Game_Minutes"]
	header += ["Pass_Count"]
	header += ["Total Distance"]
	header += ["Net X Distance"]
	header += ["Player Position Sequence"]
	header += ["Elapsed_Time"]
	header += ["Tempo"]
	header += ["Total_Velocity"]
	header += ["Vertical_Velocity"]

	output = open(output_filename, "a")
	writer = csv.writer(output, lineterminator="\n")

	writer.writerow(header)

	for g in game_list:
		game_uuid = g.uuid
		game_date = g.date

		g_diagnostics = game_diagnostics(g, team)
		for diagnostics in g_diagnostics:
			r = []
			r += [game_date]
			r += [game_uuid]
			r += [str(g)]
			r += [team_uuid]
			r += [str(team)]
			r += [seconds_to_game_time(diagnostics[8],"float")]
			r += [diagnostics[7]]
			r += [diagnostics[6]]
			r += [diagnostics[5]]
			r += [diagnostics[10]]
			r += [diagnostics[9]]
			r += [tempo_from_pass_diagnostics(diagnostics)]
			r += [total_velocity_from_pass_diagnostics(diagnostics)]
			r += [vertical_velocity_from_pass_diagnostics(diagnostics)]

			if len(header) != len(r):
				raise Exception("Rows you're about to print are not same dimension as header. Check this!")
			writer.writerow(r)

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

def is_in_range(value, low_lim, up_lim, limits="Inclusive"):
	"""Check if a value is bewteen a lower and upper limit"""
	if limits == "Inclusive":
		if low_lim <= value <= up_lim:
			return True
		else:
			return False
	elif limits == "Exclusive":
		if low_lim < value < up_lim:
			return True
		else:
			return False

def is_inside_box(event_stat):
	"""Method to determine if an event takes place inside the box"""

	player = event_stat.player
	x = event_stat.x
	y = event_stat.y

	attacking_box_x = [83, 100]
	attacking_box_y = [21.1,78.9]

	if is_in_range(x, attacking_box_x[0], attacking_box_x[1]):
		if is_in_range(y, attacking_box_y[0], attacking_box_y[1]):
			return True
	return False

def is_event_qualifier_233(event):
	"""Boolean of whether an event contains Qualifier 233"""
	for e in Qualifier.objects.filter(event_statistic=event):
		if e.qualifier_id == 233:
			return True

	return False

def find_related_event(event):
	"""Find the event_id of a related event"""
	value = None

	for q in Qualifier.objects.filter(event_statistic=event):
		if q.qualifier_id == 55:
			value = q.value

	return value

def list_index(list, value):
	"""Return the index in the list that houses the value"""
	return list.index(value)

def is_aerial_duel(event_list, team):
	"""Returns if the event list is 2 events representing an aerial duel"""
	count = 0
	for e in event_list[:2]:
		if e.type_id == 44:
			count += 1
	
	if count == 2:
		return True
	else:
		return False

def is_gk_save(event_list, team):
	"""Returns if the event list is 1 event representing an opposition GK save"""
	is_save = False
	is_saved = False
	for e in event_list[:1]:
		if e.type_id == 10:
			return True
	#check if a self miss is recorded before the opponent GK save
	for e in event_list[:2]:
		if e.type_id == 10 and e.team != team:
			is_save = True
		if e.type_id == 15 and e.team == team:
			is_saved = True

	return is_saved and is_save

def is_gk_save_and_aerial_duel(event_list, team):
	"""Returns if event list is 3; a save + a duel"""
	save = False
	duel = 0
	for e in event_list[:3]:
		if e.type_id == 10:
			save = True
		elif e.type_id == 44:
			duel += 1

	return save and duel == 2

def is_successful_take_on(event_list, team):
	"""Returns if event list has a player taking on an opponent in the front"""
	take_on = False
	missed_challenge = False

	for e in event_list[:2]:
		if e.type_id == 3 and e.team == team:
			take_on = True
		if e.type_id == 45 and e.team != team:
			missed_challenge = True

	return take_on and missed_challenge


def is_oppo_tackle_and_self_dispossessed(event_list, team):
	"""Returns if event list has an attacking player losing possession due to opponent tackle"""
	tackle = False
	disposessed = False

	for e in event_list[:2]:
		if e.type_id == 50 and e.team == team:
			disposessed = True
		if e.type_id == 7 and e.team != team:
			tackle = True

	return tackle and disposessed

def is_self_tackle_and_oppo_dispossessed(event_list, team):
	"""Returns if event list has an attacking player losing possession due to opponent tackle"""
	tackle = False
	disposessed = False

	for e in event_list[:2]:
		if e.type_id == 50 and e.team != team:
			disposessed = True
		if e.type_id == 7 and e.team == team:
			tackle = True

	return tackle and disposessed
def is_tackle(event_list, team):
	"""Returns if event list has an attacking player losing possession due to opponent tackle"""
	tackle = False

	for e in event_list[:1]:
		if e.type_id == 7 and e.team != team:
			tackle = True

	return tackle 

def is_ball_recovery(event_list, team):
	"""Returns if event list has a ball recovery in the front"""
	recovery = False
	for e in event_list[:1]:
		if e.type_id == 49:
			recovery = True

	return recovery

def is_keeper_sweeper(event_list, team):
	"""Returns if event list has keeper sweeper event in the front"""
	keeper_sweeper = False
	for e in event_list[:1]:
		if e.type_id == 59:
			keeper_sweeper = True
			
	return keeper_sweeper

def is_cross_not_claimed(event_list, team):
	"""Returns if event list has a cross-not-claimed Goalkeeper event; cross not successfully caught"""
	cnc = False
	for e in event_list[:1]:
		if e.type_id == 53:
			cnc = True
			
	return cnc

def is_opponent_player_error(event_list, team):
	"""Returns if event list has an opponent error"""
	error = False
	for e in event_list[:1]:
		if e.type_id == 51 and e.team != team:
			error = True
			
	return error

def ball_touch_intent(event_list, team):
	"""Returns intentnional or unintentional if the event is a ball touch"""
	intent = None

	for e in event_list[:1]:
		if e.type_id == 61 and e.outcome == 1 and e.team != team:
			intent = "Oppo. Intentional Ball Touch"
		elif e.type_id == 61 and e.outcome == 0 and e.team != team:
			intent = "Oppo. Unitentional Ball Touch"
		elif e.type_id == 61 and e.outcome == 1 and e.team == team:
			intent = "Intentional Ball Touch"
		elif e.type_id == 61 and e.outcome == 0 and e.team == team:
			intent = "Unintentional Ball Touch"
	return intent

def is_oppo_dispossessed(event_list, team):
	"""Returns whether an opponent is disposessed"""
	disposessed = False
	for e in event_list[:1]:
		if e.type_id == 50 and e.team != team:
			disposessed = True
			
	return disposessed

def is_self_saved(event_list, team):
	"""Returns whether self team had a shot that was saved"""
	is_true = False
	for e in event_list[:1]:
		if e.type_id == 15 and e.team == team:
			is_true = True
			
	return is_true

def is_oppo_clearance_from_self_pass(event_list, team):
	"""Returns whether an opponent cleared the ball after self was passing"""
	clearance = False
	self_pass = False
	for e in event_list[:2]:
		if e.type_id == 12 and e.team != team:
			clearance = True
		if e.type_id == 1 and e.team == team:
			self_pass = True
			
	return clearance and self_pass

def is_oppo_clearance(event_list, team):
	"""Returns whether an opponent cleared the ball"""
	clearance = False
	for e in event_list[:1]:
		if e.type_id == 12 and e.team != team:
			clearance = True

	return clearance

def is_oppo_pass(event_list, team):
	"""Returns whether an opponent passed the ball (likely a bad pass)"""
	oppo_pass = False
	for e in event_list[:1]:
		if e.type_id == 1 and e.team != team and e.outcome == 0:
			oppo_pass = True
			
	return oppo_pass

def is_missed_shot(event_list, team):
	"""Returns whether the self team missed a shot"""
	is_true = False
	for e in event_list[:1]:
		if e.type_id == 13 and e.team == team:
			is_true = True
			
	return is_true

def is_self_corner(event_list, team):
	"""Returns whether the team had a corner"""
	is_self_corner = False
	for e in event_list[:2]:
		if e.type_id == 6 and e.team == team and e.outcome == 1:
			is_self_corner = True
			
	return is_self_corner

def is_oppo_interception(event_list, team):
	"""Returns whether the opponent intercepted the ball"""
	is_true = False
	for e in event_list[:1]:
		if e.type_id == 8 and e.team != team:
			is_true = True

	return is_true

def is_self_interception(event_list, team):
	"""Returns whether the self team intercepted the ball"""
	is_true = False
	for e in event_list[:1]:
		if e.type_id == 8 and e.team == team:
			is_true = True

	return is_true


def is_post(event_list, team):
	"""Returns whether the self team shot off post"""
	is_true = False
	for e in event_list[:1]:
		if e.type_id == 14 and e.team == team:
			is_true = True

	return is_true

def is_blocked_pass(event_list, team):
	"""Returns whether the opponent blocked the ball"""
	is_true = False
	for e in event_list[:1]:
		if e.type_id == 74 and e.team != team:
			is_true = True

	return is_true

def is_gk_claim(event_list, team):
	"""Returns whether the opponent GK claimed the ball"""
	is_true = False
	for e in event_list[:1]:
		if e.type_id == 11 and e.team != team:
			is_true = True

	return is_true

def is_card_and_foul(event_list, team):
	"""Returns whether the opponent fouled"""
	is_foul = False
	is_card = False
	for e in event_list[:2]:
		if e.type_id == 17 and e.team != team:
			is_card = True
		elif e.type_id == 4 and e.team != team:
			is_foul = True

	return is_card and is_foul

def is_pk(event_list, team):
	"""Returns if there is a PK"""
	is_true = False
	for e in event_list[:1]:
		if e.type_id == 58 and e.team != team:
			is_true = True

	return is_true


def is_foul_on_opponent(event_list, team):
	"""Returns foul on opponent"""
	is_foul = False
	is_foul_pt2 = False

	for e in event_list[:2]:
		if e.type_id == 4 and e.outcome == 0 and e.team != team:
			is_foul = True
		elif e.type_id == 4 and e.outcome == 1 and e.team == team:
			is_foul_pt2 = True
	return is_foul and is_foul_pt2

def is_delayed_game(event_list, team):
	"""Looks further back due to paused game"""
	is_delayed = False
	for e in event_list[:2]:
		if e.type_id == 28:
			is_delayed = True

	return is_delayed

def is_GKsave_same_min_and_sec(event_stat_1, key_event_stat):
	"""Returns true if the two events are exact same game minute / second"""
	min_1 = event_stat_1.minute
	sec_1 = event_stat_1.second
	min_key = key_event_stat.minute
	sec_key = key_event_stat.second

	event_stat_1.type_id

	return min_1 == min_key and sec_1 == sec_key and event_stat_1.type_id == 10


def event_translator(event, include_event=False):
	"""Uses logic of below, but just an individual event by backtracking"""
	backtracked_events = backtrack(event, include_event=include_event)
	event_team = event.team

	return event_translator_eventlist(backtracked_events, event_team)

def event_translator_eventlist(backtracked_events, key_event_team):
	"""Add event translating logic to a set of events prior to input event"""
	if is_aerial_duel(backtracked_events, key_event_team):
		return "Aerial Duel"
	elif is_gk_save(backtracked_events, key_event_team):
		# print backtracked_events
		# print backtracked_events[0].game
		return "Oppo. GK Save"
	elif is_gk_save_and_aerial_duel(backtracked_events, key_event_team):
		return "Aerial Duel + Oppo. GK Save"
	elif is_successful_take_on(backtracked_events, key_event_team):
		return "Successful Take-On"
	elif is_ball_recovery(backtracked_events, key_event_team):
		return "Ball Recovery"
	elif is_keeper_sweeper(backtracked_events, key_event_team):
		return "Oppo. Keeper Sweeper"
	elif is_cross_not_claimed(backtracked_events, key_event_team):
		return "Oppo. Cross Not Claimed"
	elif is_opponent_player_error(backtracked_events, key_event_team):
		return "Oppo. Player Error"
	elif is_oppo_dispossessed(backtracked_events, key_event_team):
		return "Oppo. Dispossessed"
	elif ball_touch_intent(backtracked_events, key_event_team):
		return ball_touch_intent(backtracked_events, key_event_team)
	elif is_oppo_clearance_from_self_pass(backtracked_events, key_event_team):
		return "Oppo. Clearance from Self Passing"
	elif is_oppo_clearance(backtracked_events, key_event_team):
		return "Oppo. Clearance"
	elif is_oppo_pass(backtracked_events, key_event_team):
		return "Oppo. Pass"
	elif is_self_corner(backtracked_events, key_event_team):
		return "Attacking Corner"
	elif is_oppo_interception(backtracked_events, key_event_team):
		return "Oppo. Interception"
	elif is_self_interception(backtracked_events, key_event_team):
		return "Interception"
	elif is_blocked_pass(backtracked_events, key_event_team):
		return "Oppo. Blocked Pass"
	elif is_card_and_foul(backtracked_events, key_event_team):
		return "Oppo. Foul + Card -> Free Kick"
	elif is_foul_on_opponent(backtracked_events, key_event_team):
		return "Oppo. Foul -> Free Kick"
	elif is_gk_claim(backtracked_events, key_event_team):
		passes = get_pass_chain_count(backtracked_events[0], oppo_team_event=True)
		if passes == 0:
			return "Oppo. GK Claim"
		else:
			return "%s passes + Oppo. GK Claim" % (passes)
	elif is_oppo_tackle_and_self_dispossessed(backtracked_events, key_event_team):
		return "Oppo. Tackle and Self Dispossessed"	
	elif is_self_tackle_and_oppo_dispossessed(backtracked_events, key_event_team):
		return "Self Tackle and Oppo. Dispossessed"	
	elif is_pk(backtracked_events, key_event_team):
		return "Penalty Kick"
	elif is_missed_shot(backtracked_events, key_event_team):
		return "Missed Shot"
	elif is_self_saved(backtracked_events, key_event_team):
		return "Shot Saved"
	elif is_tackle(backtracked_events, key_event_team):
		return "Oppo. Tackle"
	elif is_delayed_game(backtracked_events, key_event_team):
		return "Delayed Game"
	elif is_post(backtracked_events, key_event_team):
		return "Shot off post"
	else:
		print "Uhoh..."
		print backtracked_events
		raise Exception("Note: couldn't identify events in the above")

def backtrack(key_event, mins=2, is_reversed=True, include_event=False):
	"""Given an event, backtrack "mins" through the eventfeed and return everything up to event"""
	game = key_event.game
	ref_minute = key_event.minute
	events = EventStatistic.objects.filter(game=game, minute__gte=ref_minute-mins, minute__lte=ref_minute)
	desired_events = []
	# print ">>>>> backtrack"

	# print "key_event = " + str(key_event)
	# print ""
	for e in events:
		# print e
		if e.uuid == key_event.uuid:
			#include this if we want the key_event included at end of list
			if include_event:
				desired_events.append(e) 
			break
		#else, ignore if event is a GK save and is at the exact same minute / second
		#note.. this would only kick out events listed before the shot, as the break 
		#above wouldn't allow those after to be considered 
		elif is_GKsave_same_min_and_sec(e, key_event):
			continue
		#else, ignore if event is type_id = 43 = deleted event
		elif is_type_id(e, 43): 
			continue
		else:
			desired_events.append(e)

	if is_reversed:
		desired_events.reverse()

	# print desired_events
	# print "<<<<<<< end backtrack"
	return desired_events

def get_pass_chain_count(input_event, include_event=False, oppo_team_event=False):
	"""Given a single event, look at the last minute of events 
	in reverse order (i.e. last to first) and find the number of passes 
	leading up to the single input event"""
	backtracked = backtrack(input_event, include_event=include_event)

	pass_count = 0
	#for when the input into get_pass_chain_count is a self-team event
	if not oppo_team_event:
		for item in backtracked:
			#if it's the same team's pass event, count it
			if item.type_id == 1 and item.team == input_event.team:
				pass_count += 1
			#if it's the same team's loose ball recovery, don't break out of the chain
			elif item.type_id == 49 and item.team == input_event.team:
				continue
			#if it's anything else, end the pass count chain
			else:
				break
	#for when the input into get_pass_chain_count is an opponent-team event
	else:
		for item in backtracked:
			#if it's the not oppo-team's pass event, count it
			if item.type_id == 1 and item.team != input_event.team:
				pass_count += 1
			#if it's the not oppo-team's loose ball recovery, don't break out of the chain
			elif item.type_id == 49 and item.team != input_event.team:
				continue
			#if it's anything else, end the pass count chain
			else:
				break
	return pass_count

def parse_backtrack(key_event, list_of_events):
	"""Given a backtracked list of events, prior to a key event, what is the cause?"""
	#check if there is an event tied to the key event using Opta Qualifiers
	key_event_team = key_event.team
	key_event_type_id = key_event.type_id
	related_event_id = find_related_event(key_event) 
	related_event = None
	between_events = None
	shot_inside_box = is_inside_box(key_event)

	output = ""
	#if there is a related event, find the events between the key and related
	if related_event_id:
		related_event = EventStatistic.objects.get(team=key_event_team, game=key_event.game, event_id=related_event_id)

		index = list_index(list_of_events, related_event)

		#if the related event is not immidiately preceding the key event
		if index != 0:
			between_events = list_of_events[0:index]

	#if there's a related event and between events
	if related_event and between_events:
		#are there passes leading up to related event?
		pass_count = get_pass_chain_count(related_event, include_event=True)
		#if not, identify what happened before the related event
		if pass_count == 0:
			leadup_related_event = event_translator(related_event, include_event=True)
			leadup_between_events = event_translator_eventlist(between_events, key_event_team)
			
			
			output = "%s then %s, %s" % (leadup_related_event, leadup_between_events, shot_inside_box)
		#if so, count those passes and then identify the events between
		elif pass_count == 1:
			leadup_between_events = event_translator_eventlist(between_events, key_event_team)

			output = "%s pass then %s, %s" % (pass_count, leadup_between_events, shot_inside_box)
		else:
			leadup_between_events = event_translator_eventlist(between_events, key_event_team)

			output = "%s passes then %s, %s" % (pass_count, leadup_between_events, shot_inside_box)
	#if there's a related event but nothing between it and the key event
	elif related_event and not between_events:
		#are there passes leading up to related event?
		pass_count = get_pass_chain_count(related_event, include_event=True)
		#if no passes, identify what happened before the related event
		if pass_count == 0:
			leadup_related_event = event_translator(related_event, include_event=True)
			
			output = "%s, %s" % (leadup_related_event, shot_inside_box)
		elif pass_count == 1:
			output = "%s pass, %s" % (pass_count, is_inside_box(key_event))
		else:
			output = "%s passes, %s" % (pass_count, is_inside_box(key_event))
	#else, there no related event (and thus no between event)
	else:
		#are there passes leading up to key event?
		pass_count = get_pass_chain_count(key_event)
		if pass_count == 0:
			leadup_key_event = event_translator(key_event)
			
			output = "%s, %s" % (leadup_key_event, shot_inside_box)
		elif pass_count == 1:
			output = "%s pass, %s" % (pass_count, shot_inside_box)
		else:
			output = "%s passes, %s" % (pass_count, shot_inside_box)

	print output + ", type_id = " + str(key_event_type_id)
