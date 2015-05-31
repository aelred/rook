import django.test.runner
import selenium.webdriver as selenium_webdriver

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
