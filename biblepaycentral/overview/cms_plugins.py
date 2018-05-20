import requests
import json
import datetime
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from biblepaycentral.biblepay.clients import BiblePayRpcClient
from biblepaycentral.podc.models import Leaderboard
from django.utils.translation import ugettext_lazy as _
from biblepaycentral.overview.statistics import get_masternode_count, get_masternode_revenue, get_masternode_rio_percent, get_exchanges, get_last_transactions, get_last_blocks, get_nextsuperblock_proposal_data


@plugin_pool.register_plugin
class OverviewBlockMasternodes(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/overviewblock_masternodes.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        context.update({
            'rio': get_masternode_rio_percent(),
            'revenue': get_masternode_revenue(),
            'masternodecount': get_masternode_count()
        })

        return context

@plugin_pool.register_plugin
class OverviewBlockMarket(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/overviewblock_market.html"
    cache = True
    
    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        r = requests.get('https://api.coinmarketcap.com/v1/ticker/biblepay/')
        context.update({
            'data': r.json()
        })

        return context

@plugin_pool.register_plugin
class OverviewBlockExchanges(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/overviewblock_exchanges.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        context.update({
            'exchanges': get_exchanges(),
        })

        return context

@plugin_pool.register_plugin
class OverviewBlockPools(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/overviewblock_pools.html"
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
class OverviewBlockBlockchain(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/overviewblock_blockchain.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        context.update({
            'last_blocks': get_last_blocks(count=7),
            'last_transaction': get_last_transactions(count=8),
        })

        return context

@plugin_pool.register_plugin
class OverviewBlockPoDC(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/overviewblock_podc.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        
        next_budget = 0
        try:
            client = BiblePayRpcClient('main')
            next_budget = client.getboincinfo()['NextSuperblockBudget']
        except:
            raise        
        
        next_superblock = 0
        try:
            client = BiblePayRpcClient('main')
            next_superblock = client.getboincinfo()['NextSuperblockHeight']
        except:
            pass        
        
        context.update({
            'team_members': Leaderboard.objects.all().count(),
            'next_budget': next_budget,
            'next_superblock': next_superblock,
            'leaderboard': Leaderboard.objects.all().order_by('-rac')[0:3]
        })
        return context

@plugin_pool.register_plugin
class OverviewBlockProposals(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/overviewblock_proposals.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        superblock_data = get_nextsuperblock_proposal_data()
        
        context.update({
            'data': superblock_data
        })
        return context

@plugin_pool.register_plugin
class OverviewBlockAPI(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/overviewblock_api.html"
    cache = True
