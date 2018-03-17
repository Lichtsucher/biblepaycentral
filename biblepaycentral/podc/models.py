import uuid
from django.db import models

class RosettaUser(models.Model):
    username = models.CharField(max_length=200, default="UNKNOWN")

class Leaderboard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    rosettauser = models.ForeignKey(RosettaUser)
    rac = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    machine_count = models.IntegerField(default=0)
    total_procs = models.IntegerField(default=0)
    task_turnaround = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    inserted_at = models.DateTimeField(auto_now_add=True)
    