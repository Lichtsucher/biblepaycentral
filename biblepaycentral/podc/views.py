import datetime
from django.db.models import Q
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from biblepaycentral.biblepay.clients import BiblePayRpcClient
from biblepaycentral.podc.models import RosettaUser, Superblock, SuperblockReceiver
from biblepaycentral.core.tools import estimate_blockhittime

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