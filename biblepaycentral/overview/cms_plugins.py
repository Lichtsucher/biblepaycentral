import requests
import json
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _

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