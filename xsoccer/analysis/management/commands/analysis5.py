"""
Objectives / Roadmap:
Types of analysis possible:
- Compare player to past version of himself:
	PoI = player
	Interest Period = current Date range
	Comparison Player Pool = player
	Comparison period = past date range

- Compare player to players of similar "cost":
	PoI = player
	interest period = date range
	comparison player pool = players within a salary band, of the same position
	comparison period = interest period's date range

- Compare player to teammates
	PoI = player
	interest period = date range
	comparison player pool = players on the team
	comparison period = interest period's date range


INPUTS:
- Player of Interest
- Comparison Player Pool
- Interest Period (start / end dates)
- Comparison Period (start / end dates)
- KPIs to measure


PROCESS:
For Interest Period:
	find all PoI's games 
	for each KPI, find PoI's per90 KPI values 
		search through game list
		aggregate per90 KPI across all games
		return list of all per90 data points

	return dictionary of: {KPI : [list of points]} 

For Comparison Period:
	for each CP:
		find all CP's games
		for each KPI, find CP's avg per90 KPI
			search through game list
			aggregate per90 KPI across all games
		return dictionary of {KPI : [list of points]}
	
	return dictionary of {KPI : {player : [list of points]}}

Create lists of summary values:
	Interest:
		List of KPI per90 points across time period

	Comparison
		List of all player's per90 points across time period

Run 2 sample T-test
	inputs:
		1) PoI KPI values
		2) list of CPs KPI values

OUTPUT:
T-test showing t-score of PoI in Post Period

"""

"""
Sample Run Script: python manage.py analysis5 --print_to_csv

"""

import datetime
import csv
import os
import time

from django.core.management.base import BaseCommand, CommandError
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
import utils.f24_analysis as uf24
import utils.f9_analysis as uf9
import utils.stats as ustats

class Command(BaseCommand):
	help = 'Pull the statistics of a team across a time-range; classify by outcome'

	def add_arguments(self,parser):
		# add optional print to csv flag
		# parser.add_argument(
		# 	"--team_uuid",
  #           dest="team_uuid",
  #           default="",
  #           help="Desried Opta team ID",
  #           )
		parser.add_argument(
			"--print_to_csv",
			action="store_true",
            dest="print_to_csv",
            default=False,
            help="save file?",
            )
		# parser.add_argument(
		# 	"--start_date",
  #           dest="start_date",
  #           default='1900-01-01',
  #           help="Example format: 1900-01-31",
  #           )
		# parser.add_argument(
		# 	"--end_date",
  #           dest="end_date",
  #           default='2900-01-01',
  #           help="Example format: 1900-01-31",
  #           )
	def handle(self,*args,**options):
		#handle import parameters

		is_print_to_csv = options["print_to_csv"]
		is_print_diagnostic = False

		#KPIs of interest
		KPIs = [
		"goals"
		,"d_kpi__pass_accuracy_%"
		]

		#interest player
		arg_ip_uuid = "p179384"
		# mullins = "p116661"
		# acosta = "p179384"

		#interest time period
		itp_start = datetime.datetime.strptime("2016-07-20", "%Y-%m-%d")
		itp_end = datetime.datetime.strptime("2016-12-01", "%Y-%m-%d")
		
		#comparison player list
		arg_cp_uuid = None
		#arg_cp_uuid = ["p116661", "p1710", "p18770", "p17279"]
		arg_cp_uuid = ["p179384"]
		#queried_player_pool = Player.objects.filter(position="Striker")

		#comparison time period
		ctp_start = datetime.datetime.strptime("2016-01-20", "%Y-%m-%d")
		ctp_end = datetime.datetime.strptime("2016-07-19", "%Y-%m-%d")

		#load players
		db_i_player = Player.objects.get(uuid=arg_ip_uuid)
		db_c_players = []
		#if we choose to load players via uuid strings
		if arg_cp_uuid:
			for p in arg_cp_uuid:
				db_c_players.append(Player.objects.get(uuid=p))
		elif queried_player_pool:
			for p in queried_player_pool:
				db_c_players.append(p)




		"""Print Summary Report to Terminal"""
		print "\nSUMMARY"
		print "Interest:"
		print "%s" % (db_i_player)
		print "%s to %s" % (itp_start, itp_end)

		print "\nComparison:"
		print "Viable comparison pool = %s players" % (len(db_c_players))
		# for p in db_c_players:
		# 	print "\t%s" % (p)
		print "%s to %s" % (ctp_start, ctp_end)

		#Pull Interest and Comparison Period Information
		interest_values = uf9.timeframe_player_stat_list_values(db_i_player, itp_start, itp_end, KPIs)
		comparison_values = uf9.timeframe_player_list_stat_list_values(db_c_players, ctp_start, ctp_end, KPIs)




		"""Print Diagnostic Report to Terminal, if of interest"""
		#Interest Period Information
		if is_print_diagnostic:
			print "---------------\n"
			print "INTEREST VALUES"
			for key in interest_values:
				print key
				print "  %s \n\t%s" % (db_i_player, interest_values[key])

		#Comparison Period Information
		if is_print_diagnostic:
			print "\nCOMPARISON VALUES"
			for key in comparison_values:
				print key
				for k in comparison_values[key]:
					print "  %s \n\t%s" % (k, comparison_values[key][k])
		


		"""Calculate and Print Results Report to Terminal"""

		print "\n---------------\n"
		print "RESULTS"

		#Calculate T Test and print results for each KPI 
		uf9.kpi_ttest(KPIs, db_i_player, interest_values, comparison_values, appearance_threshold=True)
		
