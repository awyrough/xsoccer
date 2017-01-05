### Read from F9 files and construct Teams models
import utils.xmls as xml_utils
import utils.unicode as unicode_utils
import os

from venues.models import Venue

from django.core.management.base import BaseCommand

def is_venue(xml_obj):
    """Return true if the XML object has a Team tag"""
    return xml_obj.tag == "Venue"

class Command(BaseCommand):
    """
    Sample usage:
    python manage.py build_venue_table_ALL_FILES \
        --dry_run \
        --data_filepath=data/f9/
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
            "--data_filepath",
            dest="data_filepath",
            type=str,
            required=True,
            help="Filename with data",
            )

    def handle(self, *args, **options):
        data_filepath = options["data_filepath"]
        is_dry_run = options["dry_run"]

        print "Importing venues from %s" % data_filepath
        if is_dry_run:
            print "This is a dry run and will not save any data"
        
        for root_dir, sub_dirs, filenames in os.walk(data_filepath):
            for f in filenames:
                xml_file = os.path.join(data_filepath, f)

                new_venues = []

                xml_data_root = xml_utils.get_root_from_file(xml_file)

                for child in xml_utils.get_children(xml_data_root):
                    # Iterate over each item
                    for item in xml_utils.get_children(child):
                        if is_venue(item) == False:
                            continue
                        name = xml_utils.get_tag(item, "Name").text
                        name = unicode_utils.remove_accents(name)
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
