### Read from F24 files and construct EventStatistic models
import utils.xmls as xml_utils
import datetime
import os
import time

from teams.models import Team
from games.models import Game
from players.models import Player
from eventstatistics.models import EventStatistic
from qualifiers.models import Qualifier

from django.core.management.base import BaseCommand

def is_tag(xml_obj, tag):
	"""Return true if the XML object is the Tag"""
	return xml_obj.tag == tag

def is_tag_and_type(xml_obj, tag, type):
	"""Return true if the XML object is of the right Tag and Type"""
	return xml_obj.tag == tag and xml_utils.get_attrib_if_exists(xml_obj,"Type") == type


class Command(BaseCommand):
	"""
	Sample usage:
	python manage.py build_eventstatistic_table_ALL_FILES \
		--dry_run \
		--data_filepath=data/f24/
	"""
	help = "Populate game table"

	def add_arguments(self, parser):
		"""Add custom CLI arguments"""
		parser.add_argument(
			"--dry_run",
			action="store_true",
			dest="dry_run",
			default=False,
			help="Don't save and just print teams",
			)

		parser.add_argument(
			"--data_filepath",
			dest="data_filepath",
			type=str,
			required=True,
			help="Filepath containing all data files to load",
			)

	def handle(self, *args, **options):
		temp = time.time()
		script_start = time.time()
		data_filepath = options["data_filepath"]
		is_dry_run = options["dry_run"]
		
		print "xyz 1 = " + str(time.time() - temp)
		temp = time.time()

		print "Importing EventStatistics and Qualifiers from %s" % (data_filepath)

		if is_dry_run:
			print "This is a dry run and will not save any data"
		event_pull_count = 0
		event_saved_count = 0
		q_pull_count = 0
		q_saved_count = 0
		file_count = 0

		print "xyz 2 = " + str(time.time() - temp)
		temp = time.time()

		for root_dir, sub_dirs, filenames in os.walk(data_filepath):
			for f in filenames:
				print "xyz 3 = " + str(time.time() - temp)
				temp = time.time()

				file_start = time.time()
				print file_start

				file_count += 1
				if file_count > 2:
					break
				file_event_saved_count = 0
				file_q_saved_count = 0

				xml_file = os.path.join(data_filepath, f)

				print "xyz 4 = " + str(time.time() - temp)
				temp = time.time()
				#Open up F24 and find root: <Games>
				xml_data_root = xml_utils.get_root_from_file(xml_file)

				print "xyz 5 = " + str(time.time() - temp)
				temp = time.time()
				#Find <Game>
				xml_Game = xml_utils.get_tag(xml_data_root, "Game")
				print "xyz 6 = " + str(time.time() - temp)
				temp = time.time()
				game_uuid = xml_utils.get_attrib_if_exists(xml_Game, "id")
				print "xyz 7 = " + str(time.time() - temp)
				temp = time.time()
				db_Game = Game.objects.get(uuid="f"+game_uuid)
				print "xyz 8 = " + str(time.time() - temp)
				temp = time.time()
				#Iterate through <Game> and only pay attention to <Event>s
				for xml_Event in xml_utils.get_children(xml_Game):
					print "xyz 9 = " + str(time.time() - temp)
					temp = time.time()
					if is_tag(xml_Event, "Event") == False:
						continue #skip if not the relevant <Event> child
					print "xyz 10 = " + str(time.time() - temp)
					temp = time.time()
					event_uuid = xml_utils.get_attrib_if_exists(xml_Event, "id")
					print "xyz 11 = " + str(time.time() - temp)
					temp = time.time()
					event_id = xml_utils.get_attrib_if_exists(xml_Event, "event_id")
					print "xyz 12 = " + str(time.time() - temp)
					temp = time.time()
					player_id = xml_utils.get_attrib_if_exists(xml_Event, "player_id")
					print "xyz 13 = " + str(time.time() - temp)
					temp = time.time()
					# if player_id:
					# 	db_Player = Player.objects.get(uuid="p"+player_id)
					# else:
					# 	db_Player = None

					# team_id = xml_utils.get_attrib_if_exists(xml_Event, "team_id")
					# db_Team = Team.objects.get(uuid="t"+team_id)
					# type_id = xml_utils.get_attrib_if_exists(xml_Event, "type_id")
					# period_id = xml_utils.get_attrib_if_exists(xml_Event, "period_id")
					# minute = xml_utils.get_attrib_if_exists(xml_Event, "min")
					# second = xml_utils.get_attrib_if_exists(xml_Event, "sec")
					# outcome = xml_utils.get_attrib_if_exists(xml_Event, "outcome")
					# x_coord = xml_utils.get_attrib_if_exists(xml_Event, "x")
					# y_coord = xml_utils.get_attrib_if_exists(xml_Event, "y")
					# timestamp = xml_utils.get_attrib_if_exists(xml_Event, "timestamp")
					# timestamp = datetime.datetime.strptime(timestamp,'%Y-%m-%dT%H:%M:%S.%f')

					# assist = xml_utils.get_attrib_if_exists(xml_Event, "assist")
					# if assist:
					# 	assist = True
					# else:
					# 	assist = False
					
					# keypass = xml_utils.get_attrib_if_exists(xml_Event, "keypass")
					# if keypass:
					# 	keypass = True
					# else:
					# 	keypass = False

					# new_event_statistic = EventStatistic(
					# 			uuid=event_uuid
					# 			,event_id=event_id
					# 			,game=db_Game
					# 			,player=db_Player
					# 			,team=db_Team
					# 			,type_id=type_id
					# 			,period_id=period_id
					# 			,minute=minute
					# 			,second=second
					# 			,outcome=outcome
					# 			,assist=assist
					# 			,keypass=keypass
					# 			,x=x_coord
					# 			,y=y_coord
					# 			#,timestamp=timestamp
					# 			)

					event_pull_count += 1
					# if is_dry_run == False:
					# 	new_event_statistic.save()
					# 	event_saved_count += 1
					# 	file_event_saved_count += 1
					print "xyz 15 = " + str(time.time() - temp)
					temp = time.time()
					for xml_Qualifier in xml_utils.get_children(xml_Event):
						if is_tag(xml_Qualifier, "Q") == False:
							continue #skip if not the relevant <Q> child


					# 	q_uuid = xml_utils.get_attrib_if_exists(xml_Qualifier, "id")
					# 	qualifier_id = xml_utils.get_attrib_if_exists(xml_Qualifier, "qualifier_id")
					# 	value = xml_utils.get_attrib_if_exists(xml_Qualifier, "value")

					# 	new_qualifier = Qualifier(
					# 		event_statistic=new_event_statistic
					# 		,uuid=q_uuid
					# 		,qualifier_id=qualifier_id
					# 		,value=value
					# 		)

						q_pull_count += 1

					# 	if is_dry_run == False:
					# 		new_qualifier.save()
					# 		q_saved_count += 1
					# 		file_q_saved_count += 1
					print "xyz 16 = " + str(time.time() - temp)
					temp = time.time()

				file_end = time.time()
				print file_end
				print "# files parsed = %s;   saved EventStats = %s;   saved Qs = %s;   file time = %s secs;   closing %s..." \
							% (str(file_count), file_event_saved_count, file_q_saved_count, (file_end - file_start), f)
						

		print "\n# event-statistics pulled from files = %s" % (str(event_pull_count))
		print "# event-statistics actually saved to DB = %s" % (str(event_saved_count))
		print "\n# qualifiers pulled from files = %s" % (str(q_pull_count))
		print "# qualifiers actually saved to DB = %s" % (str(q_saved_count))

		script_end = time.time()
		print "\n%s minutes to complete script" % ((script_end - script_start) / 60)