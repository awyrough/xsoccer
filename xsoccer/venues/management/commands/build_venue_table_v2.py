### Read from F40 files and construct Venues models
import utils.xmls as xml_utils
import utils.unicode as unicode_utils

from venues.models import Venue

from django.core.management.base import BaseCommand

def is_venue(xml_obj):
    """Return true if the XML object has a Team tag"""
    return xml_obj.tag == "Venue"

def is_tag(xml_obj, tag):
    """Return true if the XML object is the Tag"""
    return xml_obj.tag == tag

class Command(BaseCommand):
    """
    Sample usage:
    python manage.py build_venue_table_v2 \
        --dry_run \
        --data_filename=data/f40/squads-2016.xml
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


        print "Importing venues from %s" % data_filename
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
                if is_tag(item, "Team"):
                    # Iterate over the children within <Team> objects
                    for i in xml_utils.get_children(item):
                        new_venues = []
                        #skip if not the relevant <Stadium> child
                        if is_tag(i, "Stadium") == False:
                            continue 

                        uuid = xml_utils.get_attrib(i, "uID")
                        uuid = "v" + uuid

                        capacity = xml_utils.pull_text_if_exists(i,
                                                                "Capacity",
                                                                "")
                        name = xml_utils.pull_text_if_exists(i,
                                                                "Name",
                                                                "")
                        name = unicode_utils.remove_accents(name)


                        venue = Venue(name=name, uuid=uuid, capacity=capacity)
                        new_venues.append(venue)

                        # get all existing uuids
                        existing_venue_uuids = Venue.objects.all().values_list("uuid")

                        # log out for audit and save if not dry run and it is a new venue
                        for venue in new_venues:
                            print venue.__dict__
                            if is_dry_run == False and venue.uuid not in existing_venue_uuids:
                                venue.save()