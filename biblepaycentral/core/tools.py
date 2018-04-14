import datetime
from cache_memoize import cache_memoize
from biblepaycentral.biblepay.clients import BiblePayRpcClient

@cache_memoize(timeout=3600)
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