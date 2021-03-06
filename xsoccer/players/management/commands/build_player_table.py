# coding: utf-8

### Read from F40 file and construct Players models
import utils.xmls as xml_utils
import utils.unicode as unicode_utils
import datetime

from players.models import Player

from django.core.management.base import BaseCommand

def is_tag(xml_obj, tag):
    """Return true if the XML object is the Tag"""
    return xml_obj.tag == tag

def is_team(xml_obj):
    """Return true if the XML object has a Team tag"""
    return xml_obj.tag == "Team"

def is_player(xml_obj):
    """Return true if the XML object has a Player tag"""
    return xml_obj.tag == "Player"

class Command(BaseCommand):
    """
    Note: will want to load 2016 season first, then 2015 
        (to keep the latest version of player info)

    Sample usage:
    python manage.py build_player_table \
        --dry_run \
        --data_filename=data/f40/squads-2016.xml
    """
    help = "Populate player table"

    def add_arguments(self, parser):
        """Add custom CLI arguments"""
        parser.add_argument(
            "--dry_run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Don't save and just print players",
            )

        parser.add_argument(
            "--data_filename",
            dest="data_filename",
            type=str,
            required=True,
            help="Filename with data",
            )

    def handle(self, *args, **options):
        data_filename = options["data_filename"]
        is_dry_run = options["dry_run"]

        new_players = []
        print "Importing players from %s" % data_filename
        if is_dry_run:
            print "This is a dry run and will not save any data"

        #Open up F40 and find root: <SoccerFeed>
        xml_data_root = xml_utils.get_root_from_file(data_filename)

        new_player_count = 0
        # Iterate over the children within <SoccerFeed>
        for child in xml_utils.get_children(xml_data_root):
            if is_tag(child, "SoccerDocument") == False:
                continue #skip if not the relevant <SoccerDocument> child
            
            # Iterate over the children within <SoccerDocument>
            for item in xml_utils.get_children(child):
                if is_tag(item, "Team"):
                    # Iterate over the children within <Team> objects
                    for i in xml_utils.get_children(item):
                        #skip if not the relevant <Player> child
                        if is_tag(i, "Player") == False:
                            continue 

                        uuid = xml_utils.get_attrib(i, "uID")
                        first_name = xml_utils.pull_text_if_exists(i,
                                                                   "Stat", 
                                                                   "first_name")
                        first_name = unicode_utils.remove_accents(first_name)
                        last_name = xml_utils.pull_text_if_exists(i, 
                                                                  "Stat", 
                                                                  "last_name")
                        last_name = unicode_utils.remove_accents(last_name)
                        known_name = xml_utils.pull_text_if_exists(i, 
                                                                  "Stat", 
                                                                  "known_name")
                        if known_name:
                            known_name = unicode_utils.remove_accents(known_name)
                        birth_place = xml_utils.pull_text_if_exists(
                            i, 
                            "Stat",
                            "birth_place")
                        birth_date = xml_utils.pull_text_if_exists(i,
                            "Stat",
                            "birth_date")
                        if birth_date is None:
                            birth_date = "1900-01-01"
                        birth_date = datetime.datetime.strptime(birth_date,"%Y-%m-%d").date()
                        nationality = xml_utils.pull_text_if_exists(
                            i,
                            "Stat",
                            "first_nationality")
                        weight = xml_utils.pull_text_if_exists(i, "Stat", "weight")
                        height = xml_utils.pull_text_if_exists(i, "Stat", "height")
                        position = xml_utils.pull_text_if_exists(i, 
                                                                 "Stat", 
                                                                 "real_position")
                        position_side = xml_utils.pull_text_if_exists(
                            i,
                            "Stat",
                            "real_position_side")
                        country = xml_utils.pull_text_if_exists(i,
                                                                "Stat",
                                                                "country")

                        player = Player(uuid=uuid,
                                        first_name=first_name,
                                        last_name=last_name,
                                        known_name=known_name,
                                        birth_place=birth_place,
                                        birth_date=birth_date,
                                        nationality=nationality,
                                        weight=weight,
                                        height=height,
                                        position=position,
                                        position_side=position_side,
                                        country=country)
                        new_players.append(player)
                #look through the PlayerChanges additions
                if is_tag(item,"PlayerChanges"):
                    for i in xml_utils.get_children(item):
                        if is_tag(i,"Team"):
                            for ii in xml_utils.get_children(i):
                                if is_tag(ii,"Player"):
                                    uuid = xml_utils.get_attrib(ii, "uID")
                                    first_name = xml_utils.pull_text_if_exists(ii,
                                                                               "Stat", 
                                                                               "first_name")
                                    first_name = unicode_utils.remove_accents(first_name)
                                    last_name = xml_utils.pull_text_if_exists(ii, 
                                                                              "Stat", 
                                                                              "last_name")
                                    last_name = unicode_utils.remove_accents(last_name)
                                    known_name = xml_utils.pull_text_if_exists(ii, 
                                                                              "Stat", 
                                                                              "known_name")
                                    if known_name:
                                        known_name = unicode_utils.remove_accents(known_name)
                                    birth_place = xml_utils.pull_text_if_exists(
                                        ii, 
                                        "Stat",
                                        "birth_place")
                                    birth_date = xml_utils.pull_text_if_exists(ii,
                                        "Stat",
                                        "birth_date")
                                    if birth_date is None:
                                        birth_date = "1900-01-01"
                                    birth_date = datetime.datetime.strptime(birth_date,"%Y-%m-%d").date()
                                    nationality = xml_utils.pull_text_if_exists(
                                        ii,
                                        "Stat",
                                        "first_nationality")
                                    weight = xml_utils.pull_text_if_exists(ii, "Stat", "weight")
                                    height = xml_utils.pull_text_if_exists(ii, "Stat", "height")
                                    position = xml_utils.pull_text_if_exists(ii, 
                                                                             "Stat", 
                                                                             "real_position")
                                    position_side = xml_utils.pull_text_if_exists(
                                        ii,
                                        "Stat",
                                        "real_position_side")
                                    country = xml_utils.pull_text_if_exists(ii,
                                                                            "Stat",
                                                                            "country")

                                    player = Player(uuid=uuid,
                                                    first_name=first_name,
                                                    last_name=last_name,
                                                    known_name=known_name,
                                                    birth_place=birth_place,
                                                    birth_date=birth_date,
                                                    nationality=nationality,
                                                    weight=weight,
                                                    height=height,
                                                    position=position,
                                                    position_side=position_side,
                                                    country=country)

                                    if player not in new_players:
                                        new_players.append(player)
        

        # log out for audit and save if not dry run and it is a new team
        for player in new_players:
            # get all existing uuids
            existing_player_uuids = Player.objects.all().values_list("uuid")
            
            if is_dry_run == False and player.uuid not in [u[0] for u in existing_player_uuids]:
                player.save()
                new_player_count += 1
                print player

        print "New Players Loaded = %s" % (new_player_count)


