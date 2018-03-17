import requests
import datetime
import decimal
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from biblepaycentral.podc.models import Leaderboard, RosettaUser

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

    