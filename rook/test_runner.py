import django.test.runner
import selenium.webdriver as selenium_webdriver

import tempfile
import shutil

import settings.config
import rook.startup
import torrents.renamer

webdriver = None


class TestRunner(django.test.runner.DiscoverRunner):

    def __init__(self, driver=None, **kwargs):
        super(TestRunner, self).__init__(**kwargs)
        global webdriver
        webdriver = {
            'firefox': selenium_webdriver.Firefox,
            'phantomjs': selenium_webdriver.PhantomJS,
        }[driver]

    @classmethod
    def add_arguments(cls, parser):
        super(TestRunner, cls).add_arguments(parser)
        parser.add_argument('-w', '--webdriver', action='store',
                            dest='driver', default='firefox',
                            choices=['firefox', 'phantomjs'],
                            help='Webdriver to use')

    def setup_test_environment(self, **kwargs):
        super(TestRunner, self).setup_test_environment(**kwargs)

        # create temporary config folder
        self.prev_cfg = settings.config.DIR
        settings.config.DIR = tempfile.mkdtemp()

        # make renamer run much more frequently
        self.prev_interval = torrents.renamer.INTERVAL
        torrents.renamer.INTERVAL = 0.1

        # make sure config is read in
        rook.startup.run()

    def teardown_test_environment(self, **kwargs):
        super(TestRunner, self).teardown_test_environment(**kwargs)

        # delete temporary folder
        shutil.rmtree(settings.config.DIR)

        # reset all variables
        settings.config.DIR = self.prev_cfg
        torrents.renamer.INTERVAL = self.prev_interval

        # read in old config
        rook.startup.run()

        # stop renamer
        torrents.renamer.cancel_watch()
