"""
WRITTEN BECAUSE THERE WERE TONS OF STATISTICTYPES THAT WERE NOT DOCUMENTED ORIGINALLY BY OPTA IN THEIR ONLINE RESOURCE

NOT ACTUALLY USED TO LOAD DATA INTO DB.. THIS LIST WAS CREATED TO MODIFY THE CSV FILE AND THEN LOAD USING "build_statistictype_table.py"
"""

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
    python manage.py farm_statistictypes_forTeams \
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

        DB_stat_types = StatisticType.objects.all().values_list("opta_statistic_type_name")
        distinct_stat_types = []

        for root_dir, sub_dirs, filenames in os.walk(data_filepath):
            for f in filenames:
                file_start = time.time()

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
                    
                    if stat_type not in distinct_stat_types and stat_type not in [u[0] for u in DB_stat_types]:
                        distinct_stat_types.append(stat_type)
        
        for stat in distinct_stat_types:
            print stat

        script_end = time.time()
        print "\n%s minutes to complete script" % ((script_end - script_start) / 60)