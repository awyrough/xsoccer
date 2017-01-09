from __future__ import unicode_literals

from django.db import models


class Player(models.Model):
    """
    An Opta player. 

    Should be biographical and meta information about the player.
    """
    POSITIONS = (
        ("Goalkeeper", "Goalkeeper"),
        ("Wing Back", "Wing Back"),
        ("Full Back", "Full Back"),
        ("Central Defender", "Central Defender"),
        ("Defensive Midfielder","Defensive Midfielder"),
        ("Attacking Midfielder","Attacking Midfielder"),
        ("Central Midfielder","Central Midfielder"),
        ("Winger","Winger"),
        ("Striker","Striker"),
        ("Second Striker","Second Striker"),
        )

    POSITION_SIDES = (
        ("Left","Left"),
        ("Right","Right"),
        ("Centre","Centre"),
        ("Left/Centre","Left/Centre"),
        ("Centre/Right","Centre/Right"),
        ("Left/Centre/Right","Left/Centre/Right"),
        ("Left/Right","Left/Right"),
        )
    # Opta UUID (NB: Different than Django-generated pk/id) 
    uuid = models.CharField("Opta uID", max_length=255, unique=True)

    first_name = models.CharField("First Name", max_length=255)
    last_name = models.CharField("Last Name", max_length=255)

    known_name = models.CharField("Known Name", max_length=255, null=True)

    birth_date = models.DateField("Birth Date", null=True)
    birth_place = models.CharField("Birth Place", max_length=255, null=True)
    nationality = models.CharField("Nationality", max_length=255, null=True)
    country = models.CharField("Country", max_length=255, null=True)

    weight = models.FloatField("Weight (kg)", default=0.0, null=True)
    height = models.FloatField("Height (cm)", default=0.0, null=True)

    position = models.CharField("Real Position", choices=POSITIONS, max_length=255, null=True)
    position_side = models.CharField("Position Side of Choice", choices=POSITION_SIDES, max_length=255, null=True)

    def __str__(self):
        if self.known_name:
            return "%s (%s)" % (self.known_name, self.uuid)
        else:
            return "%s %s (%s)" % (self.first_name, 
                                             self.last_name, 
                                             self.uuid)
