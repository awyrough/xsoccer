"""
Sample Run Script: python manage.py analysis2_learning_passes --team_uuid="t1326" 
					--print_to_csv
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


class Command(BaseCommand):
	help = 'Pull the statistics of a team across a time-range; classify by outcome'

	def add_arguments(self,parser):
		# add optional print to csv flag
		parser.add_argument(
			"--team_uuid",
            dest="team_uuid",
            default="",
            help="Desried Opta team ID",
            )
		parser.add_argument(
			"--print_to_csv",
			action="store_true",
            dest="print_to_csv",
            default=False,
            help="save file?",
            )
		parser.add_argument(
			"--start_date",
            dest="start_date",
            default='1900-01-01',
            help="Example format: 1900-01-31",
            )
		parser.add_argument(
			"--end_date",
            dest="end_date",
            default='2900-01-01',
            help="Example format: 1900-01-31",
            )
	def handle(self,*args,**options):
		#handle import parameters
		if not options["team_uuid"]:
			raise Exception("Opta team ID is needed")
		is_print_to_csv = options["print_to_csv"]
		arg_team_uuid = str(options["team_uuid"])
		arg_start_date = str(options["start_date"])
		arg_end_date = str(options["end_date"])
		
		arg_start_date = datetime.datetime.strptime(arg_start_date, "%Y-%m-%d")
		arg_end_date = datetime.datetime.strptime(arg_end_date, "%Y-%m-%d")

		#load team
		db_team = Team.objects.get(uuid=arg_team_uuid)

		#pull list of games tied to the team
		team_games = ua.team_list_games(db_team, arg_start_date, arg_end_date)

		#get sample game
		sample_game = team_games[0]
		print sample_game
		#get passing chains
		pass_chains = uf24.create_pass_chains(sample_game, db_team)

		#pull statistics on passing chains
		game_diagnostics = []
		for chain in pass_chains:
			pass_chain_diagnostic_results = uf24.pass_chain_diagnostics(chain, ignore_singles=True)
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
			if pass_chain_diagnostic_results:
				game_diagnostics.append(pass_chain_diagnostic_results)

		for diagnostics in game_diagnostics:
			print "%s, %s, %s, %s, %s, %s" % (uf24.seconds_to_game_time(diagnostics[8],"float") \
				, diagnostics[7]
				, diagnostics[9]
				, uf24.tempo_from_pass_diagnostics(diagnostics)
				, uf24.total_velocity_from_pass_diagnostics(diagnostics)
				, uf24.vertical_velocity_from_pass_diagnostics(diagnostics))

		# if is_print_to_csv:	
		# 	os.chdir("/Users/Swoboda/Desktop/")

		# 	#create header row
		# 	header = ["result"] + all_stats_to_consider

		# 	output_filename = "analysis1_" + str(time.strftime('%Y_%m_%d')) + ".csv"
		# 	output = open(output_filename, "a")
		# 	writer = csv.writer(output, lineterminator="\n")

		# 	writer.writerow(header)
		
		# 	for key in results:
		# 		r = []
		# 		r += [str(ua.team_game_result(db_team, key))]
		# 		stats = results[key]
		# 		for item in all_stats_to_consider:
		# 			r += [str(stats[item])]

		# 		writer.writerow(r)

		# 	output.close()	