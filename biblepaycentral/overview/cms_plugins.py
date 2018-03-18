import requests
import json
import datetime
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from biblepaycentral.biblepay.clients import BiblePayRpcClient
from biblepaycentral.overview.models import BiblepayLastBlocksModel, BiblepayPoDCLeaderboardModel
from biblepaycentral.overview.statistics import get_masternode_count, get_masternode_revenue, get_masternode_rio_percent
from biblepaycentral.podc.models import Leaderboard


@plugin_pool.register_plugin
class BiblepayPoDCLookup(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepaypodclookup.html"
    cache = True

@plugin_pool.register_plugin
class BiblepayPoDCActiveTeamMembers(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepaypodcactiveteammembers.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context.update({
            'team_members': Leaderboard.objects.all().count()
        })
        return context

@plugin_pool.register_plugin
class BiblepayPoDCNextBudget(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepaypodcnextbudget.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        next_budget = 0
        try:
            client = BiblePayRpcClient('main')
            next_budget = client.getboincinfo()['NextSuperblockBudget']
        except:
            raise

        context.update({
            'next_budget': next_budget
        })
        return context

@plugin_pool.register_plugin
class BiblepayPoDCNextSuperblock(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepaypodcnextsuperblock.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        next_superblock = 0
        try:
            client = BiblePayRpcClient('main')
            next_superblock = client.getboincinfo()['NextSuperblockHeight']
        except:
            pass

        context.update({
            'next_superblock': next_superblock
        })
        return context

@plugin_pool.register_plugin
class BiblepayPoDCLeaderboard(CMSPluginBase):
    model = BiblepayPoDCLeaderboardModel
    render_template = "overview/cmsplugin/biblepaypodcleaderboard.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        context.update({
            'leaderboard': Leaderboard.objects.all().order_by('-rac')[0:instance.entries_count]
        })

        return context

@plugin_pool.register_plugin
class BiblepayMasternodeRIOPercent(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepaymasternoderiopercent.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        context.update({
            'rio': get_masternode_rio_percent()
        })

        return context

@plugin_pool.register_plugin
class BiblepayMasternodeRevenuePerDay(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepaymasternoderevenueperday.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        context.update({
            'revenue': get_masternode_revenue()
        })

        return context

@plugin_pool.register_plugin
class BiblepayMasternodeCount(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepaymasternodecount.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        context.update({
            'masternodecount': get_masternode_count()
        })

        return context

@plugin_pool.register_plugin
class PurepoolMiningStatistics(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/purepool_miningstatistics.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        data = {}

        try:
            r = requests.get('http://www.purepool.org/main/api/statistics')
            data = r.json()
        except:
            pass

        context.update({
            'data': data
        })

        return context

@plugin_pool.register_plugin
class BiblepayLastBlocks(CMSPluginBase):
    model = BiblepayLastBlocksModel
    render_template = "overview/cmsplugin/biblepaylastblocks.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        client = BiblePayRpcClient('main')

        current_height = client.getblockcount()

        last_blocks = []
        # get current and 5 other blocks
        for height in range(current_height, current_height-instance.entries_count, -1):
            block_hash = client.getblockhash(height)

            last_blocks.append({
                'height': height,
                'block_hash': block_hash,
            })

        context.update({
            'last_blocks': last_blocks
        })

        return context

@plugin_pool.register_plugin
class BiblepayLastTransactions(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepaylasttransactions.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

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

        context.update({
            'last_transaction': last_transaction
        })

        return context

@plugin_pool.register_plugin
class BiblepayMarketCap(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepaymarketcap.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        r = requests.get('https://api.coinmarketcap.com/v1/ticker/biblepay/')
        context.update({
            'data': r.json()
        })

        return context

@plugin_pool.register_plugin
class BiblepayExchanges(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepayexchanges.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

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


        context.update({
            'exchanges': exchanges,
        })

        return context