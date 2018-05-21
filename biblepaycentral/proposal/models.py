import uuid
from django.db import models
from django.urls import reverse

EXPENSE_TYPES = (
    ('unknown', 'UNKNOWN'),
    ('charity', 'Charity'),
    ('pr', 'PR'),
    ('p2p', 'P2P'),
    ('it', 'IT'),
)

class Proposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # time when the proposal was first added to our database
    inserted_at = models.DateTimeField(auto_now_add=True)

    # governence object id in the blockchain
    # see "biblepay-cli gobject get [gobjectid]" for details about this proposal
    gobjectid = models.CharField(max_length=100)

    # all details about the proposal in form of a hex-encoded string
    # you will find all these information decoded below. We store the string
    # if we miss to decode any information, so that we can decode them later
    hex_string = models.TextField(default="")

    # what network is for this
    network = models.CharField(max_length=20, default="unknown")

    # name of the proposal, choosen by the user
    name = models.CharField(max_length=250, default="")

    # the users biblepay address, used to send the coins to when the proposal is accepted
    receive_address = models.CharField(max_length=100, default="")

    # amount requested by the user. Can not be changed later
    amount = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    # discussion/detail url for this proposal, every proposal should have one
    url = models.CharField(max_length=250, default="")

    # the expense type can be: 
    expense_type = models.CharField(max_length=10, choices=EXPENSE_TYPES, default="unknown")

    # in theory, porposals could start end end in different times, but we don't use that
    # right now
    unix_starttime = models.IntegerField(default=0)
    unix_endtime = models.IntegerField(default=0)

    # times of the main pool related to the submission of the porposal
    prepare_time = models.DateTimeField(null=True, default=None)
    submit_time = models.DateTimeField(null=True, default=None)
    trigger_time = models.DateTimeField(null=True, default=None)
    
    # then the proposal was paid from the sancturaries
    paid_time = models.DateTimeField(null=True, default=None)

    # unclear, always empty
    funded_time = models.DateTimeField(null=True, default=None)

    # unclear
    prepare_txid = models.CharField(max_length=100, default="")

    # unclear, seems to be a copy of the gobjectid
    submit_txid = models.CharField(max_length=100, default="")

    # id of the new height/block that is the superblock
    # that paid the proposal. Is empty for not-paid proposals
    superblock_txid = models.CharField(max_length=100, default="")

    # the height of the superblock that paid the proposal
    height = models.IntegerField(null=True, default=None)

    # unclear 
    trigger_txid = models.CharField(max_length=100)

    # information if the proposal was commited from the main pool
    # to the blockchain
    prepared = models.BooleanField(default=False)
    submitted = models.BooleanField(default=False)

    # who many sanctuaries votes and what they voted
    yes_count = models.IntegerField(default=0)
    no_count = models.IntegerField(default=0)
    abstain_count = models.IntegerField(default=0)

    # yes_count - no_count = absolute_yes_count
    absolute_yes_count = models.IntegerField(default=0)

    # masternode count at the time of this proposal, relevant for the
    # absolute_yes_count, as you need to have > 10% count of the
    # masternode_count as absolute_yes_count, or the proposal is not
    # accepted in the next superblock
    masternode_count = models.IntegerField(default=0)
    
    # used to disable entries that got removed from the main pool, but we want to keep
    # them
    active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('proposals')
    
    def __str__(self):
        return '%s (%s)'% (self.name, self.expense_type)

    def is_fundable(self):
        """ returns true if the amount of absolute_yes_count is at least 10%
            of the max vote count (masternode_count) """

        if self.absolute_yes_count >= (self.masternode_count / 100) * 10:
            return True

        return False

