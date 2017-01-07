### Read from F9 files and construct PlayerStatistic models
import utils.xmls as xml_utils
import datetime
import os
import time

from teams.models import Team
from games.models import Game
from playerstatistics.models import PlayerStatistic
from venues.models import Venue
from players.models import Player
from statistictypes.models import StatisticType

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
    python manage.py build_playerstatistic_table_ALL_FILES \
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
        script_start = time.time()
        data_filepath = options["data_filepath"]
        is_dry_run = options["dry_run"]

        
        print "Importing PlayerStatistics from %s" % data_filepath
        if is_dry_run:
            print "This is a dry run and will not save any data"

        potential_save_count = 0
        saved_count = 0
        pull_count = 0
        file_count = 0
        for root_dir, sub_dirs, filenames in os.walk(data_filepath):
            for f in filenames:
                file_start = time.time()

                file_count += 1
                xml_file = os.path.join(data_filepath, f)

                new_player_statistics = []

                #Open up F9 and find root: <SoccerFeed>
                xml_data_root = xml_utils.get_root_from_file(xml_file)

                #Find <SoccerDocument>
                SoccerDocument = xml_utils.get_tag(xml_data_root, "SoccerDocument")
                
                #Evaluate if the game has two SoccerDocument components; if so, ignore the repeat
                if xml_utils.get_child_count(xml_data_root, "SoccerDocument") == 2:
                    MatchData = xml_utils.get_tag(SoccerDocument, "MatchData")
                    MatchInfo = xml_utils.get_tag(MatchData, "MatchInfo")
                    match_type = xml_utils.get_attrib(MatchInfo,"MatchType")
                    if match_type == "1st Leg":
                        continue #skip the first leg if two legs in file (aka file is for 2nd leg)                        

                game_uuid = xml_utils.get_attrib(SoccerDocument, "uID")
                #Find <MatchData>
                MatchData = xml_utils.get_tag(SoccerDocument, "MatchData")

                #Iterate through <MatchData> and only pay attention to <TeamData>
                for child in xml_utils.get_children(MatchData):
                    if is_tag(child, "TeamData") == False:
                        continue #skip if not the relevant <TeamData> child
                    
                    team_uuid = xml_utils.get_attrib(child, "TeamRef")

                    PlayerLineUp = xml_utils.get_tag(child, "PlayerLineUp")

                    #Iterate over players on a team
                    for MatchPlayer in xml_utils.get_children(PlayerLineUp):
                        player_uuid = xml_utils.get_attrib(MatchPlayer,"PlayerRef")
                        #print player_uuid
                        for stats in MatchPlayer:
                            stat_type = xml_utils.get_attrib(stats, "Type")
                            #skip formation statistic; it's not really a KPI
                            if stat_type == "formation_place":
                                continue

                            value = float(stats.text)

                            playerstat = PlayerStatistic(
                                game=Game.objects.get(uuid=game_uuid)
                                ,player=Player.objects.get(uuid=player_uuid)
                                ,statistic=StatisticType.objects.get(opta_statistic_type_name=stat_type)
                                ,value=value
                                )

                            new_player_statistics.append(playerstat)
                            pull_count += 1
                            #print playerstat

                # log out for audit and save if not dry run and it is a new team
                for playerstat in new_player_statistics:
                    # get all existing uuids for this game 
                    #(don't want to get all, ever; would be too slow)
                    existing_player_stats = PlayerStatistic.objects.filter(game=Game.objects.get(uuid=game_uuid))
                    if is_dry_run == True and playerstat not in existing_player_stats:
                        potential_save_count += 1
                    elif is_dry_run == False and playerstat not in existing_player_stats:
                        playerstat.save()
                        saved_count += 1
                        print playerstat

                file_end = time.time()
                print "# files parsed = %s;   file time = %s secs;   closing %s..." % (str(file_count), (file_end - file_start), f)
                

        print "\n# player-statistics pulled from files = %s" % (str(pull_count))
        print "\n# player-statistics that would've been saved to DB = %s" % (str(potential_save_count))
        print "\n# player-statistics actually saved to DB = %s" % (str(saved_count))

        script_end = time.time()
        print "\n%s minutes to complete script" % ((script_end - script_start) / 60)