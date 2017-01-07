### Read from F9 files and construct PlayerStatistic models
import utils.xmls as xml_utils
import datetime
import os
import time

from teams.models import Team
from games.models import Game
from teamstatistics.models import TeamStatistic
from venues.models import Venue
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
    python manage.py build_teamstatistic_table_ALL_FILES \
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

        
        print "Importing TeamStatistics from %s" % data_filepath
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

                new_team_statistics = []

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

                #Find <TeamData>
                TeamData = xml_utils.get_tag(MatchData, "TeamData")
                team_uuid = xml_utils.get_attrib(TeamData, "TeamRef")

                #Iterate through <TeamData> and only pay attention to <Stat>s
                for child in xml_utils.get_children(TeamData):
                    if is_tag(child, "Stat") == False:
                        continue #skip if not the relevant <Stat> child
                    
                    stat_type = xml_utils.get_attrib(child, "Type")
                    FT_value = int(child.text)
                    #following values will be None if they aren't present (i.e. for formation)
                    FH_value = int(xml_utils.get_attrib_if_exists(child, "FH"))
                    SH_value = int(xml_utils.get_attrib_if_exists(child, "SH"))
                    ETFH_value = int(xml_utils.get_attrib_if_exists(child, "EFH"))
                    ETSH_value = int(xml_utils.get_attrib_if_exists(child, "ESH"))
                    
                    teamstat = TeamStatistic(
                        game=Game.objects.get(uuid=game_uuid)
                        ,team=Team.objects.get(team=team_uuid)
                        ,statistic=StatisticType.objects.get(opta_statistic_type_name=stat_type)
                        ,FT_value=FT_value
                        ,FH_value=FH_value
                        ,SH_value=SH_value
                        ,ETFH_value=ETFH_value
                        ,ETSH_value=ETSH_value
                        )
                    
                    new_team_statistics.append(teamstat)
                    pull_count += 1

                # log out for audit and save if not dry run and it is a new team
                for teamstat in new_team_statistics:
                    # get all existing stats for this game 
                    #(don't want to get all, ever; would be too slow)
                    existing_team_stats = TeamStatistic.objects.filter(game=Game.objects.get(uuid=game_uuid))
                    if is_dry_run == True and teamstat not in existing_team_stats:
                        potential_save_count += 1
                    elif is_dry_run == False and teamstat not in existing_team_stats:
                        teamstat.save()
                        saved_count += 1
                        print teamstat

                file_end = time.time()
                print "# files parsed = %s;   file time = %s secs;   closing %s..." % (str(file_count), (file_end - file_start), f)
                

        print "\n# team-statistics pulled from files = %s" % (str(pull_count))
        print "\n# team-statistics that would've been saved to DB = %s" % (str(potential_save_count))
        print "\n# team-statistics actually saved to DB = %s" % (str(saved_count))

        script_end = time.time()
        print "\n%s minutes to complete script" % ((script_end - script_start) / 60)