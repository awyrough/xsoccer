### Read from F9 files and construct Games models
import utils.xmls as xml_utils
import datetime
import os

from teams.models import Team
from games.models import Game
from venues.models import Venue

from django.core.management.base import BaseCommand

def is_tag(xml_obj, tag):
	"""Return true if the XML object is the Tag"""
	return xml_obj.tag == tag

def is_tag_and_type(xml_obj, tag, type):
	"""Return true if the XML object is of the right Tag and Type"""
	return xml_obj.tag == tag and xml_utils.get_attrib(xml_obj,"Type") == type
   
class Command(BaseCommand):
	"""
	Sample usage:
	python manage.py populate_game_scores_ALL_FILES \
		--dry_run \
		--data_filepath=data/f9/
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
		data_filepath = options["data_filepath"]
		is_dry_run = options["dry_run"]

		
		print "Importing game from %s" % data_filepath
		if is_dry_run:
			print "This is a dry run and will not save any data"

		for root_dir, sub_dirs, filenames in os.walk(data_filepath):
			#create dictionaries that store game uuid as key, and score as value
			away_scores = {}
			home_scores = {}

			update_count = 0

			for f in filenames:
				xml_file = os.path.join(data_filepath, f)
				new_games = []

				#Open up F9 and find root: <SoccerFeed>
				xml_data_root = xml_utils.get_root_from_file(xml_file)
				
				count_matches = 0
				for xml_SoccerDocument in xml_utils.get_children(xml_data_root):
					if is_tag(xml_SoccerDocument, "SoccerDocument"):
						count_matches += 1

				# Iterate over the children within <SoccerFeed>
				for xml_SoccerDocument in xml_utils.get_children(xml_data_root):
					if is_tag(xml_SoccerDocument, "SoccerDocument") == False:
						continue #skip if not the relevant <SoccerDocument> child
					
					#Evaluate if the game has two components; if so, ignore the repeat
					xml_MatchData = xml_utils.get_tag(xml_SoccerDocument, "MatchData")
					xml_MatchInfo = xml_utils.get_tag(xml_MatchData, "MatchInfo")
					match_type = xml_utils.get_attrib(xml_MatchInfo, "MatchType")


					if count_matches == 2 and match_type == "1st Leg":
						continue #skip the first leg if two legs in file (aka file is for 2nd leg)                        

					uuid = xml_utils.get_attrib(xml_SoccerDocument, "uID")

					# Iterate over the children within <SoccerDocument>
					for item in xml_utils.get_children(xml_SoccerDocument):
						
						# Work with the <MatchData> object
						if is_tag(item, "MatchData"):
							# Iterate over the <TeamData> children within <MatchData> object
							for i in xml_utils.get_children(item):
								#Pull information from <TeamData> children
								if is_tag(i, "TeamData"):
									if xml_utils.get_attrib(i,"Side") == "Home":
										home_score = xml_utils.get_attrib(i,"Score")
									if xml_utils.get_attrib(i,"Side") == "Away":
										away_score = xml_utils.get_attrib(i,"Score")

				home_scores[uuid] = home_score
				away_scores[uuid] = away_score

			# log out for audit and save if not dry run and it is a new team
			for game_uuid in home_scores:
				# get all existing uuids
				if is_dry_run == True:
					print "Game = %s; Home = %s; Away = %s" % (game_uuid, home_scores[game_uuid], away_scores[game_uuid])
				if is_dry_run == False:
					Game.objects.get(uuid=game_uuid).update(home_team_score=home_scores[game_uuid])
					Game.objects.get(uuid=game_uuid).update(away_team_score=away_scores[game_uuid])
					update_count += 2

		print "number of values updated = %s" % (update_count)
		print "number of games observed  = %s" % (len(home_scores))
