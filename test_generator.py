import unittest
import xml

from lxml.etree import Element

from generate import url_to_xmlcontent, is_link_in_same_domain


class TestGenerator(unittest.TestCase):

    def test_url_to_xmlcontent(self):
        url = "http://example.com"
        xml_content = url_to_xmlcontent(url)
        self.assertIsInstance(xml_content, xml.etree.ElementTree.Element, "Valid xml element")

    def test_is_link_in_same_domain(self):
        root = 'https://example.com'
        url_1 = 'https://example.com'
        url_2 = 'http://example.com'
        url_3 = '//example.com'
        url_4 = '//example.com/test/lol'
        url_5 = '//example.com?wtf=1'
        url_6 = '//example.com//test//lol'
        url_7 = '//example1.com/?site=example.com'

        self.assertTrue(is_link_in_same_domain(root, url_1))
        self.assertTrue(is_link_in_same_domain(root, url_2))
        self.assertTrue(is_link_in_same_domain(root, url_3))
        self.assertTrue(is_link_in_same_domain(root, url_4))
        self.assertTrue(is_link_in_same_domain(root, url_5))
        self.assertTrue(is_link_in_same_domain(root, url_6))
        self.assertFalse(is_link_in_same_domain(root, url_7))
