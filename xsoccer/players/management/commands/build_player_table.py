# coding: utf-8

### Read from F40 file and construct Players models
import utils.xmls as xml_utils
import utils.unicode as unicode_utils

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

        # Iterate over the children within <SoccerFeed>
        for child in xml_utils.get_children(xml_data_root):
            if is_tag(child, "SoccerDocument") == False:
                continue #skip if not the relevant <SoccerDocument> child
            
            # Iterate over the children within <SoccerDocument>
            for item in xml_utils.get_children(child):
                if is_tag(item, "Team") == False:
                    continue #skip if not the relevant <Team> child

                # Iterate over the children within <Team> objects
                for i in xml_utils.get_children(item):
                    #skip if not the relevant <Player> child
                    if is_tag(i, "Player") == False:
                        continue 

                    uuid = xml_utils.get_attrib(i, "uID")
                    first_name = xml_utils.pull_text_if_exists(i, "Stat", "first_name")
                    first_name = unicode_utils.remove_accents(first_name)
                    last_name = xml_utils.pull_text_if_exists(i, "Stat", "last_name")
                    last_name = unicode_utils.remove_accents(last_name)
                    #birth_date = xml_utils.get_tag_and_type(i, "Stat", "last_name").text
                    birth_place = xml_utils.pull_text_if_exists(i, "Stat", "birth_place")
                    nationality = xml_utils.pull_text_if_exists(i, "Stat", "first_nationality")
                    weight = xml_utils.pull_text_if_exists(i, "Stat", "weight")
                    height = xml_utils.pull_text_if_exists(i, "Stat", "height")
                    position = xml_utils.pull_text_if_exists(i, "Stat", "real_position")
                    position_side = xml_utils.pull_text_if_exists(i, "Stat", "real_position_side")
                    country = xml_utils.pull_text_if_exists(i, "Stat", "country")

                    player = Player(uuid=uuid\
                        , first_name=first_name\
                        , last_name=last_name\
                        #, birth_date=
                        , birth_place=birth_place\
                        , nationality=nationality\
                        , weight=weight\
                        , height=height\
                        , position=position\
                        , position_side=position_side\
                        , country=country)
                    new_players.append(player)

                    print player
        # # get all existing uuids
        # existing_player_uuids = Player.objects.all().values_list("uuid")

        # # log out for audit and save if not dry run and it is a new team
        # for player in new_players:
        #     print player.__dict__
        #     if is_dry_run == False and player.uuid not in existing_player_uuids:
        #         player.save()

