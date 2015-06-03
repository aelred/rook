from .base import FunctionalTest


class StyleTest(FunctionalTest):

    def test_styling_applied(self):
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
