from django.conf import settings
from biblepaycentral.core.commands import TaskCommand
from biblepaycentral.proposal.tasks import import_proposals

class Command(TaskCommand):
    help = 'Updates/imports the current proposal list from the main pool'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
  
        import_proposals.delay()