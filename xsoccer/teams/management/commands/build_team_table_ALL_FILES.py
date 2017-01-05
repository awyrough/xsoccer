### Read from F9 files and construct Teams models
import utils.xmls as xml_utils
import os

from teams.models import Team

from django.core.management.base import BaseCommand

def is_team(xml_obj):
    """Return true if the XML object has a Team tag"""
    return xml_obj.tag == "Team"

class Command(BaseCommand):
    """
    Sample usage:
    python manage.py build_team_table_ALL_FILES \
        --dry_run \
        --data_filepath=data/f9/
    """
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
            "--data_filepath",
            dest="data_filepath",
            type=str,
            required=True,
            help="Filename with data",
            )

    def handle(self, *args, **options):
        data_filepath = options["data_filepath"]
        is_dry_run = options["dry_run"]


        print "Importing teams from files in: %s" % data_filepath
        if is_dry_run:
            print "This is a dry run and will not save any data"
        
        for root_dir, sub_dirs, filenames in os.walk(data_filepath):
            for f in filenames:
                xml_file = os.path.join(data_filepath, f)

                new_teams = []
                
                xml_data_root = xml_utils.get_root_from_file(xml_file)

                for child in xml_utils.get_children(xml_data_root):
                    # Iterate over each item
                    for item in xml_utils.get_children(child):
                        if is_team(item) == False:
                            continue
                        name = xml_utils.get_tag(item, "Name").text
                        uuid = xml_utils.get_attrib(item, "uID")
                        team = Team(name=name, uuid=uuid)
                        new_teams.append(team)

                # get all existing uuids
                existing_team_uuids = Team.objects.all().values_list("uuid")

                # log out for audit and save if not dry run and it is a new team
                for team in new_teams:
                    print team.__dict__
                    if is_dry_run == False and team.uuid not in existing_team_uuids:
                        team.save()
