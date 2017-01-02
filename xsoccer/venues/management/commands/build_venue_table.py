### Read from F9 files and construct Teams models
import utils.xmls as xml_utils

from venues.models import Venue

from django.core.management.base import BaseCommand

def is_venue(xml_obj):
    """Return true if the XML object has a Team tag"""
    return xml_obj.tag == "Venue"

class Command(BaseCommand):
    """
    Sample usage:
    python manage.py build_venue_table \
        --dry_run \
        --data_filename=data/f9/srml-98-2016-f842641-matchresults.xml
    """
    help = "Populate venue table"

    def add_arguments(self, parser):
        """Add custom CLI arguments"""
        parser.add_argument(
            "--dry_run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Don't save and just print venues",
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

        new_venues = []
        print "Importing venues from %s" % data_filename
        if is_dry_run:
            print "This is a dry run and will not save any data"

        xml_data_root = xml_utils.get_root_from_file(data_filename)

        for child in xml_utils.get_children(xml_data_root):
            # Iterate over each item
            for item in xml_utils.get_children(child):
                if is_venue(item) == False:
                    continue
                name = xml_utils.get_tag(item, "Name").text
                uuid = xml_utils.get_attrib(item, "uID")
                country = xml_utils.get_tag(item, "Country").text
                venue = Venue(name=name, uuid=uuid, country=country)
                new_venues.append(venue)

        # get all existing uuids
        existing_venue_uuids = Venue.objects.all().values_list("uuid")

        # log out for audit and save if not dry run and it is a new venue
        for venue in new_venues:
            print venue.__dict__
            if is_dry_run == False and venue.uuid not in existing_venue_uuids:
                venue.save()
