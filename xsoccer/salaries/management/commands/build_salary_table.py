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
        new_salaries = []
        for salary_data in reader:
            
            if count == 0: #skip header row
                count = 1
                continue
            player = Player.objects.get(uuid=salary_data[0])
            season = int(salary_data[1])
            base_salary = float(salary_data[2])
            compensation = float(salary_data[3])

            salary_info = Salary(player=player,
                                    season=season,
                                    base_salary=base_salary,
                                    compensation=compensation)
            new_salaries.append(salary_info)


        existing_salary_info = Salary.objects.all().values_list("season")
        
        #Given this salary data is so manual, I only want to load it in once and never restate it (at least until 2017)
        if len(existing_salary_info) > 0:
            print "Salary already exists in the DB; wipe it before re-running and continuing with this..."

        else:
            for salary in new_salaries:
                print salary #print salary.__dict__
                if is_dry_run == False:
                    salary.save()
