import datetime
from django.db.models import Q
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from biblepaycentral.biblepay.clients import BiblePayRpcClient
from biblepaycentral.podc.models import RosettaUser, Superblock, SuperblockReceiver

def estimate_blockhittime(height):
    """ we try to calculate when the block will hit.
        For that, we get the current block, 500 blocks int he past, take the time between them
        and look how much time it is in the future with the same time-per-block """

    client = BiblePayRpcClient('main')

    current_height = client.getblockcount()

    dt = None
    if current_height >= height: # already at or after the superblock? then use that time
        block_hash = client.getblockhash(height)
        block = client.getblock(block_hash)
        dt = datetime.datetime.utcfromtimestamp(block['mediantime'])
    else:
        past_block_sub = 200

        block_hash = client.getblockhash(current_height)
        block = client.getblock(block_hash)
        dt_current = datetime.datetime.utcfromtimestamp(block['mediantime'])

        past_block = current_height - past_block_sub

        block_hash = client.getblockhash(past_block)
        block = client.getblock(block_hash)
        dt_past = datetime.datetime.utcfromtimestamp(block['mediantime'])

        # the avg time between two blocks is the result
        diff = (dt_current - dt_past) / past_block_sub

        # now we count how many blocks the required block is in the future
        diff_count = height - current_height

        # and we add the avgtimer per block * future blocks until the required block
        # to "now"
        dt = datetime.datetime.now() + (diff * diff_count)

    return dt

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