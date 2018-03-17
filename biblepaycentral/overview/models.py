from cms.models.pluginmodel import CMSPlugin
from django.db import models

class BiblepayPoDCLeaderboardModel(CMSPlugin):
    entries_count = models.IntegerField(default=8)

class BiblepayLastBlocksModel(CMSPlugin):
    entries_count = models.IntegerField(default=8)