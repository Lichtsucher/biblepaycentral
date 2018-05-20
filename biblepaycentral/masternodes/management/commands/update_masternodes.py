from django.conf import settings
from biblepaycentral.core.commands import TaskCommand
from biblepaycentral.masternodes.tasks import update_masternodes

class Command(TaskCommand):
    help = 'Updates the list of masternodes'

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)

        update_masternodes.delay()