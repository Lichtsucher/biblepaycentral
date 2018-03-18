import requests
import datetime
import decimal
from random import randint
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from biblepaycentral.biblepay.clients import BiblePayRpcClient
from biblepaycentral.podc.models import Leaderboard, RosettaUser, Superblock, SuperblockReceiver



class BrokenCSV(Exception):
    pass

def pool_cvs_to_list(raw):
    """ converts a cvs file form the pool to a valid python list/dict combination.
        It also ignores anything after the last line and the special <ROW> ending of
        every line

        Original:
        id|RosettaID|Username|<ROW>
        5d8a505e-efbc-4dce-8113-02b10f2c83b5|1987449|Ponfarriac|<ROW>

        Result:
        [
            {
                'id': '5d8a505e-efbc-4dce-8113-02b10f2c83b5',
                'Username': 'Ponfarriac',
                'RosettaID': '1987449',
            }
        ]

        """

    # first, we look for the last "|<ROW>". Everything after that is junk
    last_pos = raw.rfind('|<ROW>')
    raw = raw[0:last_pos]

    # the lines are marked by an ending |<ROW>', so we split them by that
    raw_lines = raw.split('|<ROW>')

    # we don't like empty lists
    if len(raw_lines) < 2:
        raise BrokenCSV
    
    # we need to extract the header line, we use it later to build the dict
    # of every line. There will be no header-line itself in the result
    raw_header = raw_lines.pop(0).strip().replace('|<ROW>', '').split('|')
    
    lines = []
    for raw_line in raw_lines:
        line_data = raw_line.strip().split('|')

        line = {}
        for pos, header in enumerate(raw_header):
            line[header] = line_data[pos]

        lines.append(line)

    return lines

@shared_task()
def import_leaderboard():
    """ The leaderboard is a list of all users of Rosetta@home in the Biblepay Team.
        It is (right now) loaded from the main pool and put into our own database """

    pool_url = 'http://pool.biblepay.org/action.aspx?action=api_leaderboard'
    r = requests.get(pool_url)
    
    # converts the result to a list/dict combination.
    # we don't catch any errors here, as the task should fail if this is not ok
    content = pool_cvs_to_list(r.content.decode('utf-8'))

    # we drop the old entries from the leaderboard
    Leaderboard.objects.all().delete()

    # and refill it
    for entry in content:
        rosettauser, created = RosettaUser.objects.get_or_create(id=entry['RosettaID'], defaults={'username': entry['Username']})

        lb = Leaderboard(
            id=entry['id'],
            rosettauser=rosettauser,
            rac=entry['RAC'],
            machine_count=entry['MachineCount'],
            total_procs=entry['TotalProcs'],
            task_turnaround=entry['TaskTurnaround'],
        )
        lb.save()

    # Finally, we load the Leaderboard sorted by RAC and save this position to the RosettaUser
    # But first we reset the old leaderboard positions
    RosettaUser.objects.all().update(leaderboard_pos=0)
    pos = 1
    for lb in Leaderboard.objects.all().order_by('-rac').values('rosettauser_id'):
        ru = RosettaUser.objects.get(pk=lb['rosettauser_id'])
        ru.leaderboard_pos = pos
        ru.save()

        pos += 1


@shared_task()
def import_superblock(import_height=None):
    """ Imports the data for the last superblock from the main pool """

    pool_url = 'http://pool.biblepay.org/action.aspx?action=api_superblock&uncache='+str(randint(0, 99999999))
    r = requests.get(pool_url)
    
    # converts the result to a list/dict combination.
    # we don't catch any errors here, as the task should fail if this is not ok
    content = pool_cvs_to_list(r.content.decode('utf-8'))

    # first, we need to know which block to import, if none was given
    if import_height is None:
        height = 0
        for entry in content:
            if int(entry['Height']) > height:
                height = int(entry['Height'])
                print(height)
    else:
        height = import_height

    # now we need to find information about our block in the list
    # and find the amount of receivers
    receiver_count = 0
    for entry in content:
        if int(entry['Height']) == height:
            receiver_count += 1
            total_rac = entry['totalrac']

    # no data found? Exit 
    if height == 0 or receiver_count == 0:
        return

    # and add some external infos
    client = BiblePayRpcClient('main')
    budget = client.getsuperblockbudget(height)
    
    # next we create the superblock, if required, and update an existing one
    superblock, created = Superblock.objects.get_or_create(height=height)
    superblock.total_rac = total_rac
    superblock.receiver_count = receiver_count
    superblock.budget = budget
    superblock.save()

    # we need to remove the entries for this block from the receiver list,
    # it there are already entries
    SuperblockReceiver.objects.filter(superblock=superblock).delete()

    # and now we add the new entries
    for entry in content:
        if int(entry['Height']) != height:
            continue

        rosettauser, created = RosettaUser.objects.get_or_create(id=entry['rosettaid'], defaults={'username': entry['name']})

        # This is the bbp share the user gets from the budget
        reward = 0
        magnitude = 0
        try:
            magnitude = decimal.Decimal(entry['magnitude'])
        except:
            pass

        if magnitude > 0:
            try:
                reward = decimal.Decimal(superblock.budget) * decimal.Decimal(magnitude / 1000)
            except:
                pass

        receiver = SuperblockReceiver(
            rosettauser = rosettauser,
            superblock = superblock,

            address = entry['address'],
            cpid = entry['cpid'],
            team = entry['team'],

            reward = reward,

            magnitude = magnitude,
            utxo_amount = entry['utxoweight'],   # reversed in the pool
            utxo_weight = entry['utxoamount'],     # reversed in the pool

            task_weight = entry['taskweight'],
            unbanked = entry['unbanked'],

            avg_rac = entry['avgrac'] or 0,
            modified_rac = entry['modifiedrac'] or 0,

            machine_count = entry['MachineCount'] or 0,
            total_procs = entry['TotalProcs'] or 0,
        )
        receiver.save()

        rosettauser.cpid = entry['cpid']
        rosettauser.address = entry['address']
        rosettauser.team = entry['team']
        rosettauser.save()
        



        