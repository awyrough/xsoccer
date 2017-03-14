"""
Objectives:
- How does a player in time period 2 compare to himself in time period 1?
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
import utils.stats as us

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

		# if not options["team_uuid"]:
		# 	raise Exception("Opta team ID is needed")
		is_print_to_csv = options["print_to_csv"]
		# arg_team_uuid = str(options["team_uuid"])
		# arg_start_date = str(options["start_date"])
		# arg_end_date = str(options["end_date"])
		
		arg_player_uuid = "p116661"

		#time period 1
		arg_tp1_start = datetime.datetime.strptime("2015-01-01", "%Y-%m-%d")
		arg_tp1_end = datetime.datetime.strptime("2016-07-01", "%Y-%m-%d")
		#time period 2
		arg_tp2_start = datetime.datetime.strptime("2016-07-01", "%Y-%m-%d")
		arg_tp2_end = datetime.datetime.strptime("2016-11-01", "%Y-%m-%d")

		#load player
		db_player = Player.objects.get(uuid=arg_player_uuid)

		#pull list of games tied to the player
		tp1_games = ua.player_list_games(db_player, arg_tp1_start, arg_tp1_end)
		tp2_games = ua.player_list_games(db_player, arg_tp2_start, arg_tp2_end)

		print "\nBaseline Time Period"
		print "%s to %s" % (arg_tp1_start, arg_tp1_end)
		print "%s games" % (len(tp1_games))

		print "\nAnalysis Time Period"
		print "%s to %s" % (arg_tp2_start, arg_tp2_end)
		print "%s games" % (len(tp2_games))
		print "\n"
		# for game in tp1_games:
		# 	print game
		# for game in tp2_games:
		# 	print game

		KPIs = [
		"fwd_pass"
		,"shot_off_target"
		,"goals"
		]

		for kpi in KPIs:
			print kpi
			tp1_kpis = uf9.gameset_player_stat_values(db_player, tp1_games, kpi)
			tp2_kpis = uf9.gameset_player_stat_values(db_player, tp2_games, kpi)
			print us.welchs_ttest(tp1_kpis, tp2_kpis)
			print ""

		"""
		TODO next:
			1) Pull KPIs per game for the db_player
			2) Store KPIs
			3) Build a z-score test 
			4) Export to R-readable format
		"""
			
