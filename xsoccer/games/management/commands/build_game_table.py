### Read from F9 files and construct Games models
import utils.xmls as xml_utils
import datetime

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
    python manage.py build_game_table --dry_run --data_filename=data/f9/srml-98-2015-f788511-matchresults.xml
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
            "--data_filename",
            dest="data_filename",
            type=str,
            required=True,
            help="Filename with data",
            )

    def handle(self, *args, **options):
        data_filename = options["data_filename"]
        is_dry_run = options["dry_run"]

        new_teams = []
        print "Importing a game from %s" % data_filename
        if is_dry_run:
            print "This is a dry run and will not save any data"

        #Open up F40 and find root: <SoccerFeed>
        xml_data_root = xml_utils.get_root_from_file(data_filename)

        # Iterate over the children within <SoccerFeed>
        for child in xml_utils.get_children(xml_data_root):
            if is_tag(child, "SoccerDocument") == False:
                continue #skip if not the relevant <SoccerDocument> child
            
            uuid = xml_utils.get_attrib(child, "uID")

            # Iterate over the children within <SoccerDocument>
            for item in xml_utils.get_children(child):
                
                # Work with the <MatchData> object
                if is_tag(item, "MatchData"):
                    # Iterate over the children within <MatchData> object
                    for i in xml_utils.get_children(item):
                        #Pull information from <MatchInfo> child
                        if is_tag(i, "MatchInfo"):
                            attendance = xml_utils.pull_text_if_exists(i,"Attendance")
                            winner = xml_utils.get_attrib(xml_utils.get_tag(i,"Result"),"Winner")
                            date = xml_utils.pull_text_if_exists(i,"Date")
                            date = datetime.datetime.strptime(date[:len(date)-5],'%Y%m%dT%H%M%S')

                        #Pull information from <Stat Type ="first_half_time"> child
                        if is_tag(i,"Stat"):
                            if is_tag_and_type(i, "Stat", "first_half_time"):
                                first_half_time = int(i.text)
                        #Pull information from <Stat Type ="second_half_time"> child
                        if is_tag(i,"Stat"):
                            if is_tag_and_type(i, "Stat", "second_half_time"):
                                second_half_time = int(i.text)
                        #Pull information from <TeamData> children
                        if is_tag(i, "TeamData"):
                            if xml_utils.get_attrib(i,"Side") == "Home":
                                home_team = xml_utils.get_attrib(i,"TeamRef")
                            if xml_utils.get_attrib(i,"Side") == "Away":
                                away_team = xml_utils.get_attrib(i,"TeamRef")
                # Work with the <Venue> object
                if is_tag(item, "Venue"):
                    venue = xml_utils.get_attrib(item,"uID")

        print "\n"
        print "attendance = ", attendance
        print "winner = ", winner
        print "date = ", date
        print "first_half_time = ", first_half_time
        print "second_half_time = ", second_half_time
        print "home_team = ", home_team
        print "away_team = ", away_team
        # game = Game(uuid=uuid,
        #                 date=date,
        #                 attendance=attendance,
        #                 venue=Venue.objects.get(uuid=venue),
        #                 home_team=Team.objects.get(uuid=home_team),
        #                 away_team=Team.objects.get(uuid=away_team),
        #                 winner=Team.objects.get(uuid=winner),
        #                 first_half_time=first_half_time,
        #                 second_half_time=second_half_time)

        # new_games.append(game)

        # # get all existing uuids
        # existing_game_uuids = Game.objects.all().values_list("uuid")

        # # log out for audit and save if not dry run and it is a new team
        # for game in new_games:
        #     print game.__dict__
        #     if is_dry_run == False and game.uuid not in [u[0] for u in existing_game_uuids]:
        #         game.save()

