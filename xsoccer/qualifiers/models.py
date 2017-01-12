from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Qualifier(models.Model):
    """
    Opta F24 event qualifiers. 
    """

    event = models.ForeignKey('eventstatistics.EventStatistic', on_delete=models.CASCADE, related_name="event_for_qualifier")
    
    uuid = models.BigIntegerField(unique=True, null=False)

    qualifier_id = models.IntegerField(null=False)

    value = models.CharField("Value", default = None, null=True, max_length=500)

    def __str__(self):
    	if value:
    		return "Q (%s) = ID #%s w/ value = (%s)" % (self.uuid, self.qualifier_id, self.value)
    	else:
    		return  "Q (%s) = ID #%s" % (self.uuid, self.qualifier_id)