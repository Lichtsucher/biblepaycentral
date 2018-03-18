from django.conf import settings
from biblepaycentral.core.commands import TaskCommand
from biblepaycentral.podc.tasks import import_superblock

class Command(TaskCommand):
    help = 'Imports the data of the last superblock from the main pool'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        parser.add_argument('--height', default=None, type=int, help='Import a specific height from the list',)

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)

        import_superblock.delay(import_height=options['height'])