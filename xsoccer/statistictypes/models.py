from __future__ import unicode_literals

from django.db import models

# Create your models here.
class StatisticType(models.Model):
    """
    A bank of all statistic types in Opta. 
    """
    sw_id = models.IntegerField("SW_Analytics_ID", null=False)
    opta_statistic_type_name = models.CharField("Stat_type_name", primary_key=True, null=False, max_length=350)
    opta_statistic_definition = models.CharField("Definition", null=False, max_length=350)

    def __str__(self):
    	return "%s" % (self.opta_statistic_type_name)

    def definition(self):
    	return "%s (id=%s): %s" % (self.opta_statistic_type_name, self.sw_id, self.opta_statistic_definition)