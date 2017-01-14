### Read from F9 files and construct Lineup models
import utils.xmls as xml_utils
import datetime
import os
import time

from teams.models import Team
from games.models import Game
from players.models import Player
from lineups.models import Lineup

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
    python manage.py build_lineup_table_ALL_FILES \
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

        
        print "Importing Lineups from %s" % data_filepath
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
                file_saved_count = 0
                xml_file = os.path.join(data_filepath, f)

                new_lineups = []

                #Open up F9 and find root: <SoccerFeed>
                xml_data_root = xml_utils.get_root_from_file(xml_file)

                #Find <SoccerDocument>
                xml_SoccerDocument = xml_utils.get_tag(xml_data_root, "SoccerDocument")
                
                #Evaluate if the game has two SoccerDocument components; if so, ignore the repeat
                if xml_utils.get_child_count(xml_data_root, "SoccerDocument") == 2:
                    xml_MatchData = xml_utils.get_tag(xml_SoccerDocument, "MatchData")
                    xml_MatchInfo = xml_utils.get_tag(xml_MatchData, "MatchInfo")
                    match_type = xml_utils.get_attrib(xml_MatchInfo,"MatchType")
                    if match_type == "1st Leg":
                        continue #skip the first leg if two legs in file (aka file is for 2nd leg)                        

                game_uuid = xml_utils.get_attrib(xml_SoccerDocument, "uID")
                db_game = Game.objects.get(uuid=game_uuid)

                #Find <MatchData>
                xml_MatchData = xml_utils.get_tag(xml_SoccerDocument, "MatchData")

                #Find <TeamData>
                for team_data in xml_utils.get_children(xml_MatchData):
                    if is_tag(team_data,"TeamData") == False:
                        continue #skip if it's not an actual <TeamData> team
                    team_uuid = xml_utils.get_attrib(team_data, "TeamRef")
                    db_team = Team.objects.get(uuid=team_uuid)

                    #Comb through <TeamData> and only pull the "formation_used" team Stat
                    team_formation = xml_utils.get_tag_and_type(team_data, "Stat", "formation_used").text

                    #Find the XML object <PlayerLinerUp>
                    xml_PlayerLineUp = xml_utils.get_tag(team_data, "PlayerLineUp")

                    #Iterate over players on a team
                    for xml_MatchPlayer in xml_utils.get_children(xml_PlayerLineUp):
                        #find player
                        player_uuid = xml_utils.get_attrib(xml_MatchPlayer,"PlayerRef")
                        db_player = Player.objects.get(uuid=player_uuid)
                        
                        #find player position
                        player_position = xml_utils.get_attrib(xml_MatchPlayer,"Position")
                        player_subposition = xml_utils.get_attrib_if_exists(xml_MatchPlayer,"SubPosition")

                        #find if player is captain
                        is_captain = xml_utils.get_attrib_if_exists(xml_MatchPlayer,"Captain")
                        if is_captain: #if it exists, make variable a True boolean
                            is_captain = True
                        else:
                            is_captain = False

                        formation_place = xml_utils.get_tag_and_type(xml_MatchPlayer, "Stat", "formation_place").text
                        if formation_place:
                            formation_place = int(formation_place)
                        else:
                            formation_place = int(0)
                        
                        lineup = Lineup(
                            game=db_game
                            ,team=db_team
                            ,player=db_player
                            ,team_formation=team_formation
                            ,player_position=player_position
                            ,player_subposition=player_subposition
                            ,is_captain=is_captain
                            ,player_formation_number=formation_place
                            )

                        new_lineups.append(lineup)
                        pull_count += 1

                # get all existing objects, just want for the game/player; 
                # this is admittedly slow for game/players where the data is already populated; shouldn't be too bad though     
                existing_lineups = Lineup.objects.filter(game=db_game)
                existing_players = [str(i.player.uuid) for i in existing_lineups]

                # log out for audit and save if not dry run and it is a new team
                for lineup in new_lineups:
                    if is_dry_run == True and lineup.player.uuid not in existing_players:
                        potential_save_count += 1
                    elif is_dry_run == False and lineup.player.uuid not in existing_players:
                        lineup.save()
                        saved_count += 1
                        file_saved_count += 1
                        #print lineup

                file_end = time.time()
                print "# files parsed = %s;   saved Lineups = %s;   file time = %s secs;   closing %s..." % (str(file_count), (file_saved_count), (file_end - file_start), f)
        
        print "\n# lineups pulled from files = %s" % (str(pull_count))
        print "\n# lineups that would've been saved to DB = %s" % (str(potential_save_count))
        print "\n# lineups actually saved to DB = %s" % (str(saved_count))

        script_end = time.time()
        print "\n%s minutes to complete script" % ((script_end - script_start) / 60)