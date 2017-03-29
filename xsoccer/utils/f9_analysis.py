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
import utils.stats as ustats

"""Explicitly Written"""
def player_stat(player, game, statistic):
	"""Simply return the QuerySet tied to a player, game, and statistic
	Value of creating this more manual step is so that we check if there 
	is more than one QuerySet returning
	"""
	#Statisitc has passed validity check, so write logic for if we are working 
	#with a traditional or derived KPI
	player_stat = PlayerStatistic.objects.filter(game=game, player=player, statistic=statistic)

	if len(player_stat) > 1:
		print player_stat
		raise Exception("This should not return multiple values: %s" % (player_stat))

	return player_stat

def player_stat_value_per90(player, game, statistic, min_playtime=9.99):
	"""For a given player and game, return the KPI of interest on a per-90 minute basis (if time dependent)"""
	is_per90_calculation = True
	p_stat_value = None

	#For Traditional KPIs
	if not is_derived_kpi(statistic):
		p_stat = player_stat(player, game, statistic)
		#if no metric for this game, return nothing
			#if player didn't play, this will be accounted for later
		if len(p_stat) == 0: 
			p_stat_value = 0 
		else:
			p_stat_value = p_stat[0].value

	#For Derived KPIs
	elif is_derived_kpi(statistic):
		formula, kpi_a, kpi_b = derived_kpi_math(statistic)

		if formula == "a/b":
			is_per90_calculation = False #for a ratio, we don't care about the time component

			#KPI A
			kpi_a_value = PlayerStatistic.objects.filter(game=game, player=player, statistic=kpi_a)
			if len(kpi_a_value) == 0:
				kpi_a_value = "empty"
			else:
				kpi_a_value = kpi_a_value[0].value

			#KPI B
			kpi_b_value = PlayerStatistic.objects.filter(game=game, player=player, statistic=kpi_b)
			if len(kpi_b_value) == 0:
				kpi_b_value = "empty"
			else:
				kpi_b_value = kpi_b_value[0].value

			#if the player didn't play and things are empty; give dummy value to continue with script
			if kpi_a_value == "empty" or kpi_b_value == "empty":
				p_stat_value = None
			#if we're legitimately pulling 0 from the database
			elif kpi_b_value == 0:
				raise Exception("You are dividing by 0 for this derived kpi: " + str(statistic))
			#actually calculate derived metric
			else:
				p_stat_value = float(kpi_a_value) / float(kpi_b_value)

		elif formula == "a/(a+b)":
			is_per90_calculation = False #for a ratio, we don't care about the time component

			#KPI A
			kpi_a_value = PlayerStatistic.objects.filter(game=game, player=player, statistic=kpi_a)
			if len(kpi_a_value) == 0:
				kpi_a_value = "empty"
			else:
				kpi_a_value = kpi_a_value[0].value

			#KPI B
			kpi_b_value = PlayerStatistic.objects.filter(game=game, player=player, statistic=kpi_b)
			if len(kpi_b_value) == 0:
				kpi_b_value = "empty"
			else:
				kpi_b_value = kpi_b_value[0].value

			#if the player didn't play and things are empty; give dummy value to continue with script
			if kpi_a_value == "empty" or kpi_b_value == "empty":
				p_stat_value = None
			#if we're legitimately pulling 0 from the database
			elif float(kpi_a_value) + float(kpi_b_value) == 0:
				raise Exception("You are dividing by 0 for this derived kpi: " + str(statistic))
			#actually calculate derived metric
			else:
				p_stat_value = float(kpi_a_value) / (float(kpi_a_value) + float(kpi_b_value))

		elif formula == "a+b":
			is_per90_calculation = True

			#KPI A
			kpi_a_value = PlayerStatistic.objects.filter(game=game, player=player, statistic=kpi_a)
			if len(kpi_a_value) == 0:
				kpi_a_value = "empty"
			else:
				kpi_a_value = kpi_a_value[0].value

			#KPI B
			kpi_b_value = PlayerStatistic.objects.filter(game=game, player=player, statistic=kpi_b)
			if len(kpi_b_value) == 0:
				kpi_b_value = "empty"
			else:
				kpi_b_value = kpi_b_value[0].value

			#if the player didn't play and things are empty; give dummy value to continue with script
			if kpi_a_value == "empty" or kpi_b_value == "empty":
				p_stat_value = None
			#if we're legitimately pulling 0 from the database
			elif float(kpi_a_value) + float(kpi_b_value) == 0:
				raise Exception("You are dividing by 0 for this derived kpi: " + str(statistic))
			#actually calculate derived metric
			else:
				p_stat_value = float(kpi_a_value) + float(kpi_b_value)
		else:
			raise Exception("Have not seen this derived kpi formula yet..")


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
	#if a player didn't play long enough in a game
	elif time_played[0].value < min_playtime:
		returned_value = None
	# COMMENTED BELOW OUT AS IT IS UNNECESSARY WITH THE ELSE STATEMENT
	# elif time_played[0].value > 0 and p_stat_value == 0:
	# 	returned_value = 0
	elif is_per90_calculation:
		returned_value = float(p_stat_value) / (time_played[0].value / 90.0)
	else:
		returned_value = p_stat_value

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

def kpi_ttest(kpi_list, interest_subject, interest_values, comparison_values, appearance_threshold=True, long_print=True):
	"""For list of KPI, set of dictionary inputs, calculate and print significances per KPI"""
	for kpi in kpi_list:
		#check this KPI will work
		is_valid_kpi(kpi)

		interest_data_points = interest_values[kpi]
		
		comparison_data_points = []
		count = 0
		for player in comparison_values[kpi]:
			# if we want to only compare against players w/ similar game appearances as the PoI
			if appearance_threshold:
				if len(comparison_values[kpi][player]) >= len(interest_data_points):
					count += 1
					comparison_data_points += comparison_values[kpi][player]
			# if we don't care about comparison players having a similar appearance amount
			else:
				count += 1
				comparison_data_points += comparison_values[kpi][player]
		#print comparison_data_points
		tstat, signif, comp_summary, interest_summary = ustats.welchs_ttest(comparison_data_points, interest_data_points)
		if count == 0:
			raise Exception("Count of players with comparison values = 0")

		#print either a lot or very little information
		if long_print:
			print "%s... %s's normalized performance: \
						\n\t%s relative to %s player(s) || Appearance Thresh. = %s \
						\n\t   w/ %s%% statistical sig. \
						\n\tinterest.. avg value = %s \t game count = %s \
						\n\tcomparis.. avg value = %s \t game count = %s" \
						% (kpi, interest_subject, round(tstat,3), count, \
							appearance_threshold, round((1-signif)*100,1), \
							interest_summary[0], float(interest_summary[1]), \
							comp_summary[0], float(comp_summary[1])/count)
		else:
			print "%s, %s, %s, %s, %s, %s, %s, %s" % (interest_subject, kpi, round(tstat,5), \
						round((1-signif)*100,1), interest_summary[0], float(interest_summary[1]), \
						comp_summary[0], float(comp_summary[1])/count)

def kpi_ttest_group_interest(kpi_list, interest_subject, interest_values, comparison_values, appearance_threshold=True):
	"""For list of KPI, set of dictionary inputs, calculate and print significances per KPI"""
	for kpi in kpi_list:
		#check this KPI will work
		is_valid_kpi(kpi)
		
		interest_data_points = []
		i_count = 0
		for player in interest_values[kpi]:
			# if we want to only compare against players w/ similar game appearances as the PoI
			if appearance_threshold:
				if len(interest_values[kpi][player]) >= len(interest_data_points):
					i_count += 1
					interest_data_points += interest_values[kpi][player]
			# if we don't care about comparison players having a similar appearance amount
			else:
				i_count += 1
				interest_data_points += interest_values[kpi][player]


		comparison_data_points = []
		c_count = 0
		for player in comparison_values[kpi]:
			# if we want to only compare against players w/ similar game appearances as the PoI
			if appearance_threshold:
				if len(comparison_values[kpi][player]) >= len(interest_data_points):
					c_count += 1
					comparison_data_points += comparison_values[kpi][player]
			# if we don't care about comparison players having a similar appearance amount
			else:
				c_count += 1
				comparison_data_points += comparison_values[kpi][player]
		#print comparison_data_points
		tstat, signif, comp_summary, interest_summary = ustats.welchs_ttest(comparison_data_points, interest_data_points)
		if c_count == 0:
			raise Exception("Count of players with comparison values = 0")
		if long_print:
			print "%s... %s's normalized performance:\n\t%s relative to %s player(s) || Appearance Thresh. = %s \
					\n\t   w/ %s%% statistical sig. \
					\n\tinterest.. avg value = %s \t game count = %s \
					\n\tcomparis.. avg value = %s \t game count = %s" \
					% (kpi, interest_subject, round(tstat,3), c_count, \
						appearance_threshold, round((1-signif)*100,1), \
						interest_summary[0], float(interest_summary[1])/i_count, \
						comp_summary[0], float(comp_summary[1])/c_count)
		else:
			print "%s, %s, %s, %s, %s, %s, %s, %s" % (interest_subject, kpi, round(tstat,5), \
						round((1-signif)*100,1), interest_summary[0], float(interest_summary[1])/i_count, \
						comp_summary[0], float(comp_summary[1])/c_count)
			
def is_valid_kpi(kpi):
	"""Given a KPI name, is it valid to run analysis5 on?
		1) does it exist as a statistic type?
		2) is it derived and do I know how to work with it?"""

	queryset = StatisticType.objects.filter(opta_statistic_type_name=kpi)

	if len(queryset) > 1:
		raise Exception("Found more than one StatisticType under the kpi: " + str(kpi))
	elif len(queryset) == 0:
		if not is_derived_kpi(kpi):
			raise Exception("Can't find the kpi: " + str(kpi))

	return True

# def is_traditional_kpi(kpi):
# 	"""Check whether input is one of the loaded PlayerStatistics from F9"""
# 	if len(StatisticType.objects.filter(opta_statistic_type_name=kpi)) == 1:
# 		return True

# 	return False

def is_derived_kpi(kpi):
	"""Check whether input is one of the derived KPIs that can be handled"""
	
	for d_kpi in derived_kpis():
		if kpi == d_kpi[0]:
			return d_kpi
	
	return None

def derived_kpis():
	"""House all known derived KPIs"""
	d_kpis = [
	#derived kpi name , math formula, relevant statisitcs to pull
	["d_kpi__pass_accuracy_%", "a/b", "accurate_pass", "total_pass"]
	,["d_kpi__open_play_pass_success_%", "a/b", "successful_open_play_pass", "open_play_pass"]
	,["d_kpi__blocked_pass_%", "a/b", "blocked_pass", "total_pass"]
	,["d_kpi__forward_pass_%", "a/b", "fwd_pass", "total_pass"]
	,["d_kpi__backward_pass_%", "a/b", "backward_pass", "total_pass"]
	,["d_kpi__leftside_pass_%", "a/b", "leftside_pass", "total_pass"]
	,["d_kpi__rightside_pass_%", "a/b", "rightside_pass", "total_pass"]
	,["d_kpi__long_pass_own_to_opp_success_%", "a/b", "long_pass_own_to_opp_success", "long_pass_own_to_opp"]
	#,["d_kpi__shot_accuracy_%", "a/b", "long_pass_own_to_opp_success", "long_pass_own_to_opp"]
	,["d_kpi__duel_win_%", "a/(a+b)", "duel_won", "duel_lost"]
	,["d_kpi__aerial_win_%", "a/(a+b)", "aerial_won", "aerial_lost"]
	,["d_kpi__launch_accuracy_%", "a/b", "accurate_launches", "total_launches"]
	,["d_kpi__long_balls_accuracy_%", "a/b", "accurate_long_balls", "total_long_pass"]
	,["d_kpi__layoffs_accuracy_%", "a/b", "accurate_layoffs", "total_layoffs"]
	,["d_kpi__back_zone_pass_accuracy_%", "a/b", "accurate_back_zone_pass", "total_back_zone_pass"]
	,["d_kpi__fwd_zone_pass_accuracy_%", "a/b", "accurate_fwd_zone_pass", "total_fwd_zone_pass"]
	,["d_kpi__touches_per_pass", "a/b", "touches", "total_pass"]
	,["d_kpi__touches_per_accurate_pass", "a/b", "touches", "accurate_pass"]
	,["d_kpi__possession_balance", "a/b","ball_recovery","poss_lost_all"]
	,["d_kpi__attempts_conceded_ibox_%", "a/(a+b)", "attempts_conceded_ibox", "attempts_conceded_obox"]
	,["d_kpi__final_third_pass_success_%", "a/b", "successful_final_third_passes", "total_final_third_passes"]
	,["d_kpi__challenge_lost_%", "a/b", "challenge_lost", "total_contest"]
	,["d_kpi__interceptions_won_%", "a/b", "interception_won", "interception"]
	,["d_kpi__headers", "a+b", "head_clearance", "head_pass"]
	,["d_kpi__poss_won_def&mid_3rd", "a+b", "poss_won_def_3rd", "poss_won_mid_3rd"]
	]
	return d_kpis

def derived_kpi_math(kpi):
	"""Return the math, and relevant other KPI to pull from DB"""
	d_kpi_info = is_derived_kpi(kpi)

	return d_kpi_info[1], d_kpi_info[2], d_kpi_info[3]


