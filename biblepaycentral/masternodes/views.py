import datetime
from django.db.models import Q
from django.conf import settings
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render, redirect
from biblepaycentral.masternodes.models import Masternode, MasternodeHistory

def masternodes(request):
    masternodes = Masternode.objects.all().order_by('-last_seen_at')
    
    status_count = {}
    for masternode in masternodes:
        if not masternode.status in status_count:
            status_count[masternode.status] = 0
        
        status_count[masternode.status] += 1
        
    content_type = ContentType.objects.get_for_model(Masternode)

    return render(request, 'masternodes/masternodes.html', {
            'masternodes': masternodes,
            'status_count': status_count,
            'content_type': content_type
        })
