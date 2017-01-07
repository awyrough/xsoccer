"""
WRITTEN BECAUSE THERE WERE TONS OF STATISTICTYPES THAT WERE NOT DOCUMENTED ORIGINALLY BY OPTA IN THEIR ONLINE RESOURCE

NOT ACTUALLY USED TO LOAD DATA INTO DB.. THIS LIST WAS TAKEN TO MODIFY THE CSV FILE AND THEN LOAD USING "build_statistictype_table.py"
"""

### Read from F9 files and construct Games models
import utils.xmls as xml_utils
import datetime
import os

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
    python manage.py farm_statistictypes \
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

        
        print "Importing PlayerStatistics from %s" % data_filepath
        if is_dry_run:
            print "This is a dry run and will not save any data"

        distinct_stat_types = []

        for root_dir, sub_dirs, filenames in os.walk(data_filepath):
            for f in filenames:
                
                xml_file = os.path.join(data_filepath, f)

                #Open up F9 and find root: <SoccerFeed>
                xml_data_root = xml_utils.get_root_from_file(xml_file)

                #Find <SoccerDocument>
                SoccerDocument = xml_utils.get_tag(xml_data_root, "SoccerDocument")

                #Find <MatchData>
                MatchData = xml_utils.get_tag(SoccerDocument, "MatchData")

                #Iterate through <MatchData> and only pay attention to <TeamData>
                for child in xml_utils.get_children(MatchData):
                    if is_tag(child, "TeamData") == False:
                        continue #skip if not the relevant <SoccerDocument> child
                    
                    PlayerLineUp = xml_utils.get_tag(child, "PlayerLineUp")

                    #Iterate over players on a team
                    for MatchPlayer in xml_utils.get_children(PlayerLineUp):
                        
                        for stats in MatchPlayer:
                            stat_type = xml_utils.get_attrib(stats, "Type")
                            #skip formation statistic; it's not really a KPI
                            if stat_type == "formation_place":
                                continue

                            if stat_type not in distinct_stat_types:
                                distinct_stat_types.append(stat_type)
        
        for stat in distinct_stat_types:
            print stat
