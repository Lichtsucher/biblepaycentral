import datetime
from collections import OrderedDict
from django.db.models import Q, Max, Min
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from biblepaycentral.biblepay.clients import BiblePayRpcClient
from biblepaycentral.proposal.models import Proposal
from biblepaycentral.core.tools import estimate_blockhittime
from biblepaycentral.overview.statistics import get_nextsuperblock_proposal_data

def proposals(request, block=None):
    """ Shows the information about proposals, the current non-backed or all of a specific block (for history infos) """
    
    network="main"

    if block is None:
        proposals_raw = Proposal.objects.filter(network=network, height__isnull=True, active=True)
        older_block = Proposal.objects.filter(network=network).aggregate(Max('height'))['height__max']
        newer_block = None
    else:
        proposals_raw = Proposal.objects.filter(network=network, height=block, active=True)
        older_block = Proposal.objects.filter(network=network, height__lt=block).aggregate(Max('height'))['height__max']
        newer_block = Proposal.objects.filter(network=network, height__gt=block).aggregate(Min('height'))['height__min']
    
    superblock_data = get_nextsuperblock_proposal_data(block=block)
    
    # we regroup the proposals into their categories
    expense_types = [['charity', 'Charity'], ['it', 'IT'], ['pr', 'PR'], ['p2p', 'P2P']]
    
    proposals = OrderedDict()
    for et in expense_types:
        proposals[et[1]] = []
        
        for prop_rar in proposals_raw:
            if prop_rar.expense_type == et[0]:
                proposals[et[1]].append(prop_rar)
    
    return render(request, 'proposal/proposals.html', {
            'requested_block': block,
            'data': superblock_data,
            'proposals': proposals,
            'older_block': older_block,
            'newer_block': newer_block,
        })

def details(request, proposal_id, network="main"):
    return render(request, 'proposal/detail.html')