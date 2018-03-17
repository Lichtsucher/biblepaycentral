from django.conf import settings
from biblepaycentral.core.commands import TaskCommand
from biblepaycentral.podc.tasks import import_leaderboard

class Command(TaskCommand):
    help = 'Replaces the current leaderboard content with new one from the Main Pool'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        
        import_leaderboard.delay()