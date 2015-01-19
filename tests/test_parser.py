import unittest
import os

from racconto.models import *
from racconto.parsers import *

def path_to(template):
    return os.path.abspath(os.path.join('tests', 'support', 'templates', template + '.md'))


class TestParse(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def parse(self, template):
        return RaccontoParser(path_to(template)).parse()

    def test_meta_and_content(self):
        page = self.parse('meta_and_content')

        self.assertIsInstance(page, Page)
        self.assertIsInstance(page.content, PageContent)
        self.assertIsInstance(page.meta, Meta)

    def test_page_meta_extraction(self):
        page = self.parse('meta_and_content')

        self.assertEqual(page.title, 'Page Title')
        self.assertEqual(page.slug, 'meta_and_content')
        self.assertEqual(page.meta.list, ['first thing', 'second thing'])

    def test_content_extraction(self):
        page = self.parse('meta_and_content')

        self.assertEqual(len(page.content), 1)
        self.assertEqual("%s" % page.content, '<p>Here are the contents</p>\n')

    def test_bad_meta(self):
        self.assertRaises(MetaBlockYAMLParseError, self.parse, 'bad_meta')

    def test_unclosed_page_meta(self):
        self.assertRaises(MetaBlockNotClosedError, self.parse, 'unclosed_page_meta')

    def test_named_section(self):
        page = self.parse('named_section')

        self.assertEqual(len(page.content), 1)
        self.assertIsInstance(page.content.my_section, Section)
        self.assertEqual("%s" % page.content.my_section, "<p>Here are the contents of my_section</p>\n")

    def test_two_named_sections(self):
        page = self.parse('two_named_sections')

        self.assertEqual(len(page.content), 2)
        self.assertEqual("%s" % page.content.my_section_1, "<p>Here are the contents of <code>my_section_1</code></p>\n")
        self.assertEqual("%s" % page.content.my_section_2, "<p>Here are the contents of <code>my_section_2</code></p>\n")

    def test_section_meta(self):
        page = self.parse('section_meta')

        self.assertEqual(len(page.content), 2)
        self.assertEqual("%s" % page.content.first, "<p>Here are the contents of first</p>\n")
        self.assertEqual("%s" % page.content.second, "<p>Here are the contents of second</p>\n")

        self.assertEqual({"some_key": "A value"}, page.content.first.meta)
        self.assertEqual({"other_key": ["list", "of things"]}, page.content.second.meta)

    def test_implicit_section_names(self):
        page = self.parse('implicit_section_names')
        sections = iter(page.content)

        self.assertEqual(len(page.content), 2)
        self.assertEqual(sections.next().name, 'section_0')
        self.assertEqual(sections.next().name, 'section_1')

    def test_bad_section_name(self):
        self.assertRaises(SectionNameError, self.parse, 'bad_section_name')



if __name__ == '__main__':
    unittest.main()

