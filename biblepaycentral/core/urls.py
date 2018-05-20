# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from biblepaycentral.podc.views import detail_user, find_user, ajax_utxreport, leaderboard
from biblepaycentral.proposal.views import proposals
from biblepaycentral.masternodes.views import masternodes

admin.autodiscover()

urlpatterns = [
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {'cmspages': CMSSitemap}}),
]

urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),  # NOQA
    
    url('podc/leaderboard/', leaderboard, name="podc_leaderboard"),
    url('podc/user/(?P<rosettaid>\d+)/', detail_user, name="podc_detail_user"),
    url('podc/find_user/', find_user, name="podc_find_user"),
    url('podc/ajax/utxoreport/(?P<cpid>.*)/', ajax_utxreport, name="podc_ajax_utxoreport"),
    
    url('masternodes/', masternodes, name="masternodes_masternodes"),
    
    url('proposals/(?P<block>\d+)/', proposals, name="proposals_height"),
    url('proposals/', proposals, name="proposals"),
    
    url(r'^', include('cms.urls')),
)

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ] + staticfiles_urlpatterns() + urlpatterns
