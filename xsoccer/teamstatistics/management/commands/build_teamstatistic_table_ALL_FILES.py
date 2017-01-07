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

def is_new_TeamStatistic(query_TS, list_from_DB):
    """Return true if the TeamStatistic is not in the DB"""
    for ts in list_from_DB:
        if (ts.game == query_TS.game) and (ts.team == query_TS.team) and (ts.statistic == query_TS.statistic):
            return False

    return True

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
                for team in xml_utils.get_children(MatchData):
                    if is_tag(team,"TeamData") == False:
                        continue #skip if it's not an actual <TeamData> team
                    team_uuid = xml_utils.get_attrib(team, "TeamRef")

                    #Iterate through <TeamData> and only pay attention to <Stat>s
                    for child in xml_utils.get_children(team):
                        if is_tag(child, "Stat") == False:
                            continue #skip if not the relevant <Stat> child
                        
                        stat_type = xml_utils.get_attrib(child, "Type")
                        value = float(child.text)
                        #following values will be None if they aren't present (i.e. for formation)
                        FH_value = xml_utils.get_attrib_if_exists(child, "FH")
                        if FH_value: 
                            FH_value = float(FH_value)
                        SH_value = xml_utils.get_attrib_if_exists(child, "SH")
                        if SH_value: 
                            SH_value = float(SH_value)
                        ETFH_value = xml_utils.get_attrib_if_exists(child, "EFH")
                        if ETFH_value: 
                            ETFH_value = float(ETFH_value)
                        ETSH_value = xml_utils.get_attrib_if_exists(child, "ESH")
                        if ETSH_value: 
                            ETSH_value = float(ETSH_value)
                        
                        teamstat = TeamStatistic(
                            game=Game.objects.get(uuid=game_uuid)
                            ,team=Team.objects.get(uuid=team_uuid)
                            ,statistic=StatisticType.objects.get(opta_statistic_type_name=stat_type)
                            ,value=value
                            ,FH_value=FH_value
                            ,SH_value=SH_value
                            ,ETFH_value=ETFH_value
                            ,ETSH_value=ETSH_value
                            )
                        
                        new_team_statistics.append(teamstat)
                        pull_count += 1

                # log out for audit and save if not dry run and it is a new team statistic
                team_stats_from_DB = TeamStatistic.objects.filter(game=Game.objects.get(uuid=game_uuid))

                for teamstat in new_team_statistics:
                    if is_dry_run == True and is_new_TeamStatistic(teamstat,team_stats_from_DB):
                        potential_save_count += 1
                        #print teamstat
                    elif is_dry_run == False and is_new_TeamStatistic(teamstat,team_stats_from_DB):
                        teamstat.save()
                        saved_count += 1
                        #print teamstat

                file_end = time.time()
                print "# files parsed = %s;   file time = %s secs;   closing %s..." % (str(file_count), (file_end - file_start), f)               

        print "\n# team-statistics pulled from files = %s" % (str(pull_count))
        print "\n# team-statistics that would've been saved to DB = %s" % (str(potential_save_count))
        print "\n# team-statistics actually saved to DB = %s" % (str(saved_count))

        script_end = time.time()
        print "\n%s minutes to complete script" % ((script_end - script_start) / 60)