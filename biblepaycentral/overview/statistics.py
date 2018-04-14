import datetime
import requests
from cache_memoize import cache_memoize
from biblepaycentral.core.tools import estimate_blockhittime
from biblepaycentral.biblepay.clients import BiblePayRpcClient
from biblepaycentral.proposal.models import Proposal

@cache_memoize(timeout=3600)
def get_nextsuperblock_proposal_data(network="main"):
    client = BiblePayRpcClient(network)

    # next superblock and budget
    sbdata = client.getgovernanceinfo()

    data = {
        'next_superblock': sbdata['nextsuperblock'],
        'next_budget': int(sbdata['nextbudget']),
    }

    # when do we expect this block?
    data['estimated_time']  = estimate_blockhittime(sbdata['nextsuperblock'])

    # budget per category
    data['budgets'] = {
        'charity': (data['next_budget'] / 100) * 50,
        'it': (data['next_budget'] / 100) * 25,
        'pr': (data['next_budget'] / 100) * 12.5,
        'p2p': (data['next_budget'] / 100) * 12.5,
    }

    # and all proposals that have not been paid by any superblock but have
    # the approval of at least 10% of all active sanctuaries. This is required to
    # be paid in the next superblock
    data['requested_budgets'] = {
        'total': 0,
        'charity': 0,
        'it': 0,
        'pr': 0,
        'p2p': 0,
        'unspend': 0,
    }

    proposals = Proposal.objects.filter(network=network, height__isnull=True)
    for proposal in proposals:
        if proposal.expense_type == 'unknown':
            continue

        if proposal.is_fundable():
            data['requested_budgets'][proposal.expense_type] += proposal.amount
            data['requested_budgets']['total'] += proposal.amount

    data['requested_budgets']['unspend'] = data['next_budget'] - data['requested_budgets']['total']
    if data['requested_budgets']['unspend'] < 0:
        data['requested_budgets']['unspend'] = 0

    # for the graph, we need the highest value in the budgets or requested_budget
    data['highest_budget_value'] = 0
    check = [data['requested_budgets'], data['budgets']]
    for c in check:
        for k, v in c.items():
            if k != 'total' and v > data['highest_budget_value']:
                data['highest_budget_value'] = int(v)

    return data

@cache_memoize(timeout=10)
def get_last_blocks(entries_count):
    client = BiblePayRpcClient('main')

    current_height = client.getblockcount()

    last_blocks = []
    # get current and 5 other blocks
    for height in range(current_height, current_height-entries_count, -1):
        block_hash = client.getblockhash(height)

        last_blocks.append({
            'height': height,
            'block_hash': block_hash,
        })

    return last_blocks

@cache_memoize(timeout=30)
def get_last_transactions():
    client = BiblePayRpcClient('main')

    height = client.getblockcount()

    current_tx = 0
    last_transaction = []

    run = True
    while run:
        block_hash = client.getblockhash(height)
        block_data = client.getblock(block_hash)


        for tx in block_data.get('tx', []):
            tx_data = client.getrawtransaction(tx, True)

            amount = 0
            for t in tx_data['vout']:
                amount += t['value']

            last_transaction.append({
                'txid': tx_data['txid'],
                'height': height,
                'block_hash': block_hash,
                'recipient_count': len(tx_data['vout']),
                'amount': amount,
                'timestamp': datetime.datetime.fromtimestamp(int(tx_data['time'])),
            })

            current_tx += 1
            if current_tx > 10:
                run = False
                break

        height -= 1

    return last_transaction

@cache_memoize(timeout=3600)
def get_exchanges():
    exchanges = []

    # CCEX.com
    usd_volume24h = 0
    usd_price = 0
    usd_price_var = 0
    btc_volume24h = 0
    btc_price = 0
    btc_price_var = 0

    try:
        data = requests.get('https://c-cex.com/t/bbp-usd.json').json()
        usd_price = data['ticker']['lastbuy']
        usd_price_var = ''

        data = requests.get('https://c-cex.com/t/volume_usd.json').json()
        usd_volume24h = data['ticker']['bbp']['vol']

        data = requests.get('https://c-cex.com/t/bbp-btc.json').json()
        btc_price = float(data['ticker']['lastbuy'])
        btc_price_var = ''

        data = requests.get('https://c-cex.com/t/volume_btc.json').json()
        btc_volume24h = data['ticker']['bbp']['vol']
    except:
        pass

    exchanges.append({
        'name': 'C-CEX.com',
        'url': 'https://c-cex.com',
        'usd_volume24h': usd_volume24h,
        'usd_price': usd_price,
        'usd_price_var': usd_price_var,
        'btc_volume24h': btc_volume24h,
        'btc_price': btc_price,
        'btc_price_var': btc_price_var,
    })

    # southxchange.com
    usd_volume24h = 0
    usd_price = 0
    usd_price_var = 0
    btc_volume24h = 0
    btc_price = 0
    btc_price_var = 0

    try:
        data = requests.get('https://www.southxchange.com/api/price/BBP/USD').json()
        usd_volume24h = data['Volume24Hr']
        usd_price = data['Last']
        usd_price_var = data['Variation24Hr']

        data = requests.get('https://www.southxchange.com/api/price/BBP/BTC').json()
        btc_volume24h = data['Volume24Hr']
        btc_price = float(data['Last'])
        btc_price_var = data['Variation24Hr']
    except:
        pass

    exchanges.append({
        'name': 'southxchange.com',
        'url': 'https://www.southxchange.com',
        'usd_volume24h': usd_volume24h,
        'usd_price': usd_price,
        'usd_price_var': usd_price_var,
        'btc_volume24h': btc_volume24h,
        'btc_price': btc_price,
        'btc_price_var': btc_price_var,
    })

    return exchanges

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

    