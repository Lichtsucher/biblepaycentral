import requests
import datetime
import decimal
from random import randint
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from biblepaycentral.biblepay.clients import BiblePayRpcClient
from biblepaycentral.masternodes.models import Masternode
from biblepaycentral.core.csv import pool_cvs_to_list

@shared_task()
def update_masternodes():
    client = BiblePayRpcClient('main')
    
    for mn in client.masternode_list_full():
        masternode, created = Masternode.objects.get_or_create(txid=mn['txid'], defaults={
                'status': mn['status'],
                'version':  mn['version'],
                'address':  mn['address'],
            })
        
        masternode.status = mn['status']
        masternode.version = mn['version']
        masternode.address = mn['address']
        masternode.last_seen_at = timezone.now()
        masternode.save()
    
        



        