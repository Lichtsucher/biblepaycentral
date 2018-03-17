import requests
from cache_memoize import cache_memoize
from biblepaycentral.biblepay.clients import BiblePayRpcClient


@cache_memoize(timeout=3600)
def get_masternode_count():
    """ asks the biblepay client for the count of masternodes """

    count = -1
    try:
        client = BiblePayRpcClient('main')
        count = len(client.rpc.masternodelist())
    except:
        pass

    return count

@cache_memoize(timeout=3600)
def get_masternode_revenue():
    """ calculates the current min masternode revenue based on live data """

    value = -1
    try:
        # first, we need the sum of all revenue per day and the block count
        r = requests.get('http://www.purepool.org/main/api/block_subsidysum/1')
        data = r.json()

        # next we need the masternode list count
        masternode_count = get_masternode_count()

        # now we calc the masternode share (including PoDC values by taking the PoW subsidity * 10)
        value = (data['sum'] * 10) / masternode_count
    except:
        pass
    
    return int(value)

@cache_memoize(timeout=3600)
def get_masternode_rio_percent():
    """ Returns the anual revenue percent for the masternodes -> How much they get by owning one """

    anual_revenue = get_masternode_revenue() * 365;

    percent = (100 / 1550001) * anual_revenue

    return int(percent)

    