"""
Objectives:
- Which players pass together the most?
- What types of position combintations are most frequent in pass-sequences?
"""

"""
Sample Run Script: python manage.py analysis3 --team_uuid="t1326" 
					--print_to_csv

					python manage.py analysis4 --team_uuid="t1326"  --start_date="2016-07-01"
					python manage.py analysis4 --team_uuid="t1326"  --start_date="2016-01-01" --end_date="2016-07-01"
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

		for game in team_games:
			print "Analyzing Passes for %s in %s" % (db_team, str(game))
			
			for item in uf24.identify_shots(game, db_team):
				#print item
				backtracked = uf24.backtrack(item)
				for i in backtracked:
					continue#print "   " + str(i)

				uf24.parse_backtrack(item, backtracked)