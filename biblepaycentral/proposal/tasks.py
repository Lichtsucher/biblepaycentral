import requests
import datetime
import decimal
from random import randint
from celery import shared_task
from django.utils import timezone
from django.conf import settings
#from biblepaycentral.biblepay.clients import BiblePayRpcClient
from biblepaycentral.proposal.models import Proposal, EXPENSE_TYPES
from biblepaycentral.core.csv import pool_cvs_to_list

def convert_poodatetime(d):
    try:
        return datetime.datetime.strptime(d, "%m/%d/%Y %I:%M:%S %p")
    except:
        pass

    return None

@shared_task()
def import_proposals():
    """ The leaderboard is a list of all users of Rosetta@home in the Biblepay Team.
        It is (right now) loaded from the main pool and put into our own database """

    pool_url = 'http://pool.biblepay.org/action.aspx?action=api_proposals'
    r = requests.get(pool_url)

    # converts the result to a list/dict combination.
    # we don't catch any errors here, as the task should fail if this is not ok
    content = pool_cvs_to_list(r.content.decode('utf-8'))
    
    # we deactivate all Proposals that are not already part of a superblock, as these can be
    # deleted at any time from the main pool. We reactivate the ones we found in the file
    # from the main pool
    Proposal.objects.filter(height__isnull=True).update(active=False)

    for line in content:
        proposal, created = Proposal.objects.get_or_create(id=line['id'], defaults={'gobjectid': line['GobjectID']})

        proposal.hex_string = line['Hex']
        proposal.network = line['Network']
        proposal.name = line['Name']
        proposal.receive_address = line['ReceiveAddress']
        proposal.amount = line['Amount']
        proposal.url = line['URL']

        proposal.expense_type = 'unknown'
        for et in EXPENSE_TYPES:
            if et[0] == line['expensetype'].lower():
                proposal.expense_type = et[0]

        proposal.unix_starttime = line['UnixStartTime']
        proposal.unix_endtime = line['UnixEndTime']

        # DateTimeFields
        proposal.prepare_time = convert_poodatetime(line['PrepareTime'])
        proposal.submit_time = convert_poodatetime(line['SubmitTime'])
        proposal.trigger_time = convert_poodatetime(line['TriggerTime'])
        proposal.paid_time = convert_poodatetime(line['PaidTime'])
        proposal.funded_time = convert_poodatetime(line['FundedTime'])

        proposal.prepare_txid = line['PrepareTXID']
        proposal.submit_txid = line['SubmitTxId']
        proposal.superblock_txid = line['SuperBlockTxId']
        proposal.trigger_txid = line['TriggerTxId']
        
        proposal.active = True

        proposal.height = None
        if line['Height'] != '':
            proposal.height = line['Height']

        # Boolean fields
        proposal.prepared = False
        if line['Prepared']:
            proposal.prepared = True

        proposal.submitted = False
        if line['Submitted']:
            proposal.submitted = True

        proposal.yes_count = line['YesCount'] or 0
        proposal.no_count = line['NoCt'] or 0
        proposal.abstain_count = line['AbstainCount'] or 0
        proposal.absolute_yes_count = line['AbsoluteYesCount'] or 0

        proposal.masternode_count = line['MasternodeCount'] or 0

        proposal.save()



"""
{


#####

'TriggerTime': '',
'SubmitTime': '3/17/2018 9:44:07 AM',
'Updated': '3/17/2018 8:35:52 AM',
'Added': '3/17/2018 8:35:52 AM',
'PrepareTime': '3/17/2018 8:35:53 AM'
'PaidTime': '',
'FundedTime': '',
'expensetype': 'PR',
'ReceiveAddress': 'BPR66Q5J1H6jyDjrnJx7BpUz1Q1HCQx4Wk',
'id': '56b50e50-27ae-42af-82cd-ce9de2418d0a',
'SuperBlockTxId': '',
'Network': 'main',
'Amount': '378333.0000',
'Name': 'Biblepay mass embracement campaign tour and meetups',
'Height': '',
'SubmitTxId': '922ae4637cd5b16b468350717e3e7393c6f097108c714957161aa4d4da37e7fb',
'PrepareTXID': '879b71881ab97ec398111f520c6ae380bdc26ae768f451ca44ce081b811a304e',
'TriggerTxId': '',
'UnixStartTime': '1521293752',
'UnixEndTime': '1521293752',
'YesCount': '21',
'MasternodeCount': '124',
'AbsoluteYesCount': '21',
'URL': 'http://forum.biblepay.org/index.php?topic=118.0',
'AbstainCount': '0',
'NoCt': '0',
'Prepared': '1',
'Submitted': '1',
'Hex': '5b5b2270726f706f73616c222c7b22656e645f65706f6368223a2231353231323933373532222c226e616d65223a224269626c65706179206d61737320656d62726163656d656e742063616d706169676e20746f757220616e64206d656574757073222c227061796d656e745f61646472657373223a22425052363651354a3148366a79446a726e4a78374270557a3151314843517834576b222c227061796d656e745f616d6f756e74223a223337383333332e3030222c2273746172745f65706f6368223a2231353231323933373532222c2274797065223a312c2275726c223a22687474703a2f2f666f72756d2e6269626c657061792e6f72672f696e6465782e7068703f746f7069633d3131382e30227d5d5d',
'GobjectID': '922ae4637cd5b16b468350717e3e7393c6f097108c714957161aa4d4da37e7fb',


'UserName': 'bible_pay',
'budgetable': '',
'UserId': 'a6cf4bda-6a7b-4e33-bcb2-cbf658dfff6d',
}
"""
    

