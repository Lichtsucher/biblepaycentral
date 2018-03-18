import uuid
from django.db import models

class RosettaUser(models.Model):
    username = models.CharField(max_length=200, default="UNKNOWN")
    cpid = models.CharField(max_length=100, default="")
    team = models.IntegerField(default=0)
    address = models.CharField(max_length=100, default="")
    leaderboard_pos = models.IntegerField(default=0)

class Leaderboard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    rosettauser = models.ForeignKey(RosettaUser)
    rac = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    machine_count = models.IntegerField(default=0)

    # total processor count = info fromt he rosetta homepage, not used in PoDC
    total_procs = models.IntegerField(default=0)
    
    task_turnaround = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    inserted_at = models.DateTimeField(auto_now_add=True)

class Superblock(models.Model):
    height = models.IntegerField(primary_key=True)
    total_rac = models.IntegerField(default=0)
    receiver_count = models.IntegerField(default=0)
    budget = models.DecimalField(max_digits=14, decimal_places=4, default=0)

class SuperblockReceiver(models.Model):
    # the superblock, of which this entry is part of
    superblock = models.ForeignKey(Superblock)

    # the rosetta user for this entry
    rosettauser = models.ForeignKey(RosettaUser)

    inserted_at = models.DateTimeField(auto_now_add=True)

    # the biblepay address connected to the rosetta account
    address = models.CharField(max_length=100)

    # the identifier for the rosetta account for external systems
    # like biblepay
    cpid = models.CharField(max_length=100)

    # the rosetta team id
    team = models.IntegerField(default=0)

    # The important number to define the share!
    # the share of the superblock in per mill(e).
    # Means: if the superblock as 500000 bbp, and the user has a magnitute of
    # 20, then the user would get 1000 bbp
    magnitude = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    # the magnitude is used as a per mile value. To make it one, we need to div it by 1000
    # This is the bbp share the user gets from the budget
    # reward = superblock-budget * ( magnitude / 1000 )
    reward = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    # the stake amount for this entry. Means the coins you they will stay in your
    # wallet for this superblock. Used to support "real" users
    utxo_amount = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    # these two numbers modify the RAC of the user. In best case.
    # They are percent values that should always be 100%, but can be lower
    # if the user doesn't have enough staking, or if something goes wrong
    # with the tasks
    utxo_weight = models.IntegerField(default=0)
    task_weight = models.IntegerField(default=0)
    
    avg_rac = models.IntegerField(default=0)
    modified_rac = models.IntegerField(default=0)

    unbanked = models.BooleanField(default=False)

    machine_count = models.IntegerField(default=0)
    total_procs = models.IntegerField(default=0)

    class Meta:
        unique_together = (("superblock", "rosettauser"),)
