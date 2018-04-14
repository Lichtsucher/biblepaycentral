import requests
import json
import datetime
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from biblepaycentral.biblepay.clients import BiblePayRpcClient
from biblepaycentral.overview.models import BiblepayLastBlocksModel, BiblepayPoDCLeaderboardModel
from biblepaycentral.overview.statistics import get_masternode_count, get_masternode_revenue, get_masternode_rio_percent, get_exchanges, get_last_transactions, get_last_blocks, get_nextsuperblock_proposal_data
from biblepaycentral.podc.models import Leaderboard



@plugin_pool.register_plugin
class BiblepayVersion(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepayversion.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        version = '0.0.0.0'
        try:
            r = requests.get('http://pool.biblepay.org/SAN/version.htm')
            version = r.content
        except:
            pass

        context.update({
            'version': version
        })
        return context

@plugin_pool.register_plugin
class BiblepayProposalsOpenList(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepayproposalsopenlist.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        context.update({
            'proposals': superblock_data
        })
        return context



@plugin_pool.register_plugin
class BiblepayProposalsNextSuperblockOverview(CMSPluginBase):
    model = CMSPlugin
    render_template = "overview/cmsplugin/biblepayproposalsnextsuperblockoverview.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        superblock_data = get_nextsuperblock_proposal_data()
        
        context.update({
            'data': superblock_data
        })
        return context

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

        last_blocks = get_last_blocks(instance.entries_count)

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

        last_transaction = get_last_transactions()

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

        exchanges = get_exchanges()

        context.update({
            'exchanges': exchanges,
        })

        return context