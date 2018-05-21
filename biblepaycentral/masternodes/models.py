import uuid
from django.db import models
from django.urls import reverse

class Masternode(models.Model):
    # every masternode is bound to one transaction that shows the
    # spend 1 500 001 bbp
    txid = models.CharField(max_length=100, primary_key=True, editable=False)
    
    # the address related to this masternode. The masternode reward is paid to this address
    address = models.CharField(max_length=64)

    # time when the masternode was first seen
    inserted_at = models.DateTimeField(auto_now_add=True)
    
    # the last time the masternode was seen (with any status)
    last_seen_at = models.DateTimeField(auto_now_add=True)

    # the status of the masternode known in the blockchain
    # One of: ENABLED, NEW_START_REQUIRED, WATCHDOG_EXPIRED, PRE_ENABLED, UPDATE_REQUIRED, EXPIRED
    status = models.CharField(max_length=30)
    
    # version of the watchdog (?)
    version = models.IntegerField()
    
    def get_absolute_url(self):
        return reverse('masternodes_masternodes')
    
    def __str__(self):
        return self.txid
    
    def save(self, *args, **kwargs):
        # we check if the current database entry is different from this entry
        # If yes, we create a history entry
        
        create_history = False
        
        try:
            db_mn = Masternode.objects.get(txid=self.txid)
            
            if db_mn.status != self.status or str(db_mn.version) != str(self.version):
                create_history = True
        except Masternode.DoesNotExist:
            create_history = True
            pass
        
        super(Masternode, self).save(*args, **kwargs)
        
        if create_history:
            history = MasternodeHistory()
            history.masternode = self
            history.status = self.status
            history.version = self.version
            history.save()
    
class MasternodeHistory(models.Model):
    masternode = models.ForeignKey(Masternode, on_delete=models.CASCADE,)
    
    # time of when his history entry was added
    inserted_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=30)
    version = models.IntegerField()