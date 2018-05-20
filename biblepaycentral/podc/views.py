import datetime
from django.db.models import Q
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from biblepaycentral.biblepay.clients import BiblePayRpcClient
from biblepaycentral.podc.models import RosettaUser, Superblock, SuperblockReceiver
from biblepaycentral.core.tools import estimate_blockhittime
from biblepaycentral.podc.models import Leaderboard

def leaderboard(request):
    leaderboard = Leaderboard.objects.all().order_by('-rac')

    return render(request, 'podc/leaderboard.html', {
            'leaderboard': leaderboard,
        })

def find_user(request):
    search_value = request.POST.get('search')

    search_value_int = -1
    try:
        search_value_int = int(search_value)
    except:
        pass

    # first, we do the exact searches
    result = RosettaUser.objects.filter(cpid=search_value).first()
    if result is not None:
        return redirect('podc_detail_user', result.id)

    result = RosettaUser.objects.filter(address=search_value).first()
    if result is not None:
        return redirect('podc_detail_user', result.id)

    result = RosettaUser.objects.filter(id=search_value_int).first()
    if result is not None:
        return redirect('podc_detail_user', result.id)

    # not found? Then try it by username
    result = RosettaUser.objects.filter(username=search_value).first()
    if result is not None:
        return redirect('podc_detail_user', result.id)

    # not found? Then try it by username
    result = RosettaUser.objects.filter(username__contains=search_value).first()
    if result is not None:
        return redirect('podc_detail_user', result.id)

    return render(request, 'podc/user_not_found.html')

def detail_user(request, rosettaid):
    """ displays the detail payment info for a user related to PoDC/Rosetta@home
        It is designed like a modern banking site """

    # the rosetta user
    rosettauser = get_object_or_404(RosettaUser, pk=rosettaid)

    # we need to know which is the most current superblock to show the
    # next payment Superblock
    superblock = Superblock.objects.all().order_by('-height').first()

    receiver = None
    superblock_time = None
    if superblock:
        try:
            receiver = SuperblockReceiver.objects.get(superblock=superblock, rosettauser=rosettauser)
        except SuperblockReceiver.DoesNotExist:
            pass

        superblock_time = estimate_blockhittime(superblock.height)
        


    # and finally, the history entries
    superblockreceiver = SuperblockReceiver.objects.exclude(superblock=superblock).filter(rosettauser=rosettauser).order_by('-superblock_id')

    return render(request, 'podc/detail_user.html', {
            'rosettauser': rosettauser,
            'superblock': superblock,
            'receiver': receiver,
            'superblockreceiver': superblockreceiver,
            'superblock_time': superblock_time,
        })


#################### AJAX

def ajax_utxreport(request, cpid):
    utxreport = []
    
    client = BiblePayRpcClient('main')
    report = client.utxoreport(cpid)
    
    prev_day = ''
    for entry in report:               
        for s in ['(', ')', '[', ']', 'TXID=']:
            entry = entry.replace(s, '')

        data = entry.split(' ')

        if len(data) < 4: # some other output in the json
            continue
        
        d = data[1].split('-')
        day = datetime.date(int(d[2]), int(d[0]), int(d[1]))

        utxreport.append({
            'block': data[0],
            'day': day.strftime("%A %d. %B %Y"),
            'time': data[2],
            'utxo_weight': data[3],
            'transaction_id': data[5],
            'new_day': False,
        })

        utxreport.sort(key=lambda e: e['block'], reverse=True)
        
    # now we add a day info
    prev_day = ''
    for i, item in enumerate(utxreport):
        new_day = False
        if item['day'] != prev_day:
            prev_day = item['day']
            new_day = True

        utxreport[i]['new_day'] = new_day

    return render(request, 'podc/ajax_utxoreport.html', {
            'utxreport': utxreport
        })