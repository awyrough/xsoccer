from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Qualifier(models.Model):
    """
    Opta F24 event qualifiers. 
    """

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name="event_for_qualifier")
    
    uuid = models.BigIntegerField(unique=True, null=False)

    qualifier_id = models.IntegerField(null=False)
    #todo(AJ): understand the range of values of qualifier IDs, by parsing all data / reading documentation

    value = models.CharField("Value", default = None, null=True)

    def __str__(self):
    	if value:
    		return "Q (%s) = ID #%s w/ value = (%s)" % (self.uuid, self.qualifier_id, self.value)
    	else:
    		return  "Q (%s) = ID #%s" % (self.uuid, self.qualifier_id)