from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from rook.test_runner import webdriver


class StyleTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_styling_applied(self):
        self.browser.get(self.live_server_url)

        # The user sizes their window
        self.browser.set_window_size(1024, 768)

        # The user sees the input box is centered
        width = self.browser.get_window_size()['width']
        inputbox = self.browser.find_element_by_id('search')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            width / 2,
            delta=5
        )
