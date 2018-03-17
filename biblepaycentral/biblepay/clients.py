import json
from bitcoinrpc.authproxy import AuthServiceProxy
from django.conf import settings

def biblepay_client_factory(network):
    """ creates and returns the biblepay client for rpc commands """
    
    conn = settings.BIBLEPAY_RPC[network]
    
    url = "http://%s:%s@%s:%s" % (conn['USER'], conn['PASSWORD'], conn['IP'], conn['PORT'])    
    return AuthServiceProxy(url)

class BlockNotFound(Exception):
    pass

class UnknownServerMessage(Exception):
    pass

class BiblePayRpcClient(object):
    """ this is a BiblePay rpc client, used in the PurePool.
        We use it to make it easier and more "python-like" in usage when needed """
    
    def __init__(self, network):
        self.rpc = biblepay_client_factory(network)

    def getblockcount(self):
        return self.rpc.getblockcount()

    def getblockhash(self, height):
        return self.rpc.getblockhash(height)

    def getboincinfo(self):
        return self.rpc.exec('getboincinfo')

    def getblock(self, block_hash):
        return self.rpc.getblock(block_hash)
    
    def getrawtransaction(self, txid, decoded=False):
        decoded_s = 0
        if decoded:
            decoded_s = 1
        return self.rpc.getrawtransaction(txid, decoded_s)