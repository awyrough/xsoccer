### Read from custom CSV file and construct Salary models
import csv
from players.models import Player

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Sample usage:
    python manage.py build_salary_table \
        --dry_run \
        --data_filename=data/opta_playerID_salary.csv
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
            "--data_filename",
            dest="data_filename",
            type=str,
            required=True,
            help="Filename with data",
            )

    def handle(self, *args, **options):
        is_dry_run = options["dry_run"]
        data_filename = options["data_filename"]
        f = open(data_filename, 'rU')
        reader = csv.reader(f)

        print "Importing salary data from %s" % data_filename
        if is_dry_run:
            print "This is a dry run and will not save any data"

        xml_data_root = xml_utils.get_root_from_file(data_filename)

        count = 0
        for salary_data in reader:
            
            if count == 0: #skip header
                count = 1
                continue
            
            date = datetime.datetime.strptime(game_data[0], "%m/%d/%y").date()
            home_team_id = game_data[1]
            home_team = Team.objects.get(sw_id=home_team_id)
            away_team = Team.objects.get(sw_id=game_data[5])
            new_game = Game.objects.create(date=date,
                                           home_team=home_team,
                                           away_team=away_team)





        # for child in xml_utils.get_children(xml_data_root):
        #     # Iterate over each item
        #     for item in xml_utils.get_children(child):
        #         if is_team(item) == False:
        #             continue
        #         name = xml_utils.get_tag(item, "Name").text
        #         uuid = xml_utils.get_attrib(item, "uID")
        #         team = Team(name=name, uuid=uuid)
        #         new_teams.append(team)

        # # get all existing uuids
        # existing_team_uuids = Team.objects.all().values_list("uuid")

        # # log out for audit and save if not dry run and it is a new team
        # for team in new_teams:
        #     print team.__dict__
        #     if is_dry_run == False and team.uuid not in existing_team_uuids:
        #         team.save()
