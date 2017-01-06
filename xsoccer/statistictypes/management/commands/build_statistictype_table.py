### Read from custom CSV file and construct statistic type models
import csv

from statistictypes.models import StatisticType

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Sample usage:
    python manage.py build_statistictype_table \
        --dry_run \
        --data_filename=data/F9_Statistic_Types.csv
    """
    help = "Populate statistic type table (for aggregate player and team stats)"

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

        print "Importing statistic type information from %s" % data_filename
        if is_dry_run:
            print "This is a dry run and will not save any data"

        count = 0
        new_statistics = []
        for data in reader:
            
            if count < 4: #skip notes and header rows
                count += 1
                continue

            sw_id = int(data[0])
            stat = data[1]
            definition = data[2]

            statistic = StatisticType(sw_id=sw_id,
                                    opta_statistic_type_name=stat,
                                    opta_statistic_definition=definition)
            new_statistics.append(statistic)


        # log out for audit and save if not dry run and it is a new team
        for statistic in new_statistics:
            # get all existing statistic IDs
            existing_statistics = StatisticType.objects.all().values_list("sw_id")
            
            if is_dry_run == False and statistic.sw_id not in [u[0] for u in existing_statistics]:
                statistic.save()
                print statistic

            elif is_dry_run == True:
                print statistic