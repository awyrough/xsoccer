### Read from F9 files and construct Teams models
import utils.xmls as xml_utils

from teams.models import Team

from django.core.management.base import BaseCommand

def is_team(xml_obj):
    """Return true if the XML object has a Team tag"""
    return xml_obj.tag == "Team"

class Command(BaseCommand):
    help = "Populate team table"

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
        print "Importing teams from %s" % data_filename
        if is_dry_run:
            print "This is a dry run and will not save any data"

        xml_data_root = xml_utils.get_root_from_file(data_filename)

        for child in xml_utils.get_children(xml_data_root):
            # Iterate over each item
            for item in xml_utils.get_children(child):
                if is_team(item) == False:
                    continue
                name = xml_utils.get_tag(item, "Name").text
                uuid = xml_utils.pull_attrib(item, "uID")
                team = Team(name=name, uuid=uuid)
                new_teams.append(team)

        for team in new_teams:
            print team.__dict__
            if is_dry_run == False:
                team.save()
