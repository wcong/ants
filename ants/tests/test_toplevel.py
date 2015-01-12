from unittest import TestCase
import six
import ants


class ToplevelTestCase(TestCase):

    def test_version(self):
        self.assertIs(type(ants.__version__), six.text_type)

    def test_version_info(self):
        self.assertIs(type(ants.version_info), tuple)

    def test_optional_features(self):
        self.assertIs(type(ants.optional_features), set)
        self.assertIn('ssl', ants.optional_features)

    def test_request_shortcut(self):
        from ants.http import Request, FormRequest
        self.assertIs(ants.Request, Request)
        self.assertIs(ants.FormRequest, FormRequest)

    def test_spider_shortcut(self):
        from ants.spider import Spider
        self.assertIs(ants.Spider, Spider)

    def test_selector_shortcut(self):
        from ants.selector import Selector
        self.assertIs(ants.Selector, Selector)

    def test_item_shortcut(self):
        from ants.item import Item, Field
        self.assertIs(ants.Item, Item)
        self.assertIs(ants.Field, Field)
