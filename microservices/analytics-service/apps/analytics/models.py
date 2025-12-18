from django.db import models
from django.utils import timezone 

class Report(models.Model):
    title = models.CharField(max_length=128)
    all_rows = models.IntegerField()
    checked = models.IntegerField()
    success = models.IntegerField()
    remarks = models.IntegerField()
    elemenated_remarks_today = models.IntegerField()
    remarks_today = models.IntegerField()
    checked_today = models.IntegerField()
    rest = models.IntegerField()
    date = models.DateField(default=timezone.now)
