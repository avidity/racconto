import unittest
import os

from racconto.models import Post, Page, PageContent, Section, Meta
from racconto.parsers import RaccontoParser


#def mocked_open(name, mode, encoding):
#    s = StringIO.StringIO()
#    s.write(templates.get(name))
#    return s

def path_to(template):
    return os.path.abspath(os.path.join('tests', 'support', 'templates', template + '.md'))


class TestParse(unittest.TestCase):
    def setUp(self):
        pass
#        with patch('codecs.open') as mocked_open:
#            s = StringIO.StringIO()
#            s.write(templates.get()
#            mocked_open.return_value = s
#
#        codecs.open = mock.MagicMock()
#        patcher = patch('codecs.open', new_callable=mocked_open)

#        self._codecs_open = codecs.openor-just-replace-method-with-mock
#        codecs.open =
#        codecs.open = mock.Mock(return_value=CodecsMock().open())

    def tearDown(self):
        pass
#        codecs.open = self._codecs_open

    def parse(self, template):
        return RaccontoParser(path_to(template)).parse()

    def test_meta_and_content(self):
        result = self.parse('meta_and_content')

        self.assertIsInstance(result, Page)
        self.assertIsInstance(result.content, PageContent)
        self.assertIsInstance(result.meta, Meta)

    def test_page_meta_extraction(self):
        result = self.parse('meta_and_content')

        self.assertEqual(result.title, 'Page Title')
        self.assertEqual(result.slug, 'meta_and_content')
        self.assertEqual(result.meta.list, ['first thing', 'second thing'])

    def test_content_extraction(self):
        result = self.parse('meta_and_content')

        self.assertEqual(len(result.content), 1)
        self.assertEqual("%s" % result.content, '<p>Here are the contents</p>\n')



# class CodecsMock():
#     """A mock class for codecs open function."""
#     def __init__(self, data):
#         self.data = data
#     def readlines(self):
#         """Return a list of lines, each line is appended with
#         newline
#         """
#         return ["%s%s" % (i
#    tem, "\n") for item in self.data.split("\n")]
#     def close(self):
#         pass

# class TestParser(unittest.TestCase):

#     def setUp(self):
#         self.valid_file_content = """---
# config: value
# other: 123
# ---

# Body of the file.
# """
#         self.invalid_file_content = "A file without YAML Front Matter."

#         self.parser = RaccontoParser()
#         self.parser.filepath = "some/path"
#         # Stash codecs.open() so we can restore after mock
#         self._codecs_open = codecs.open
#         # Stash RaccontoParser._create_[post/page] methods
#         self._create_page = self.parser._create_page
#         self._create_post = self.parser._create_post

#     def tearDown(self):
#         del self.valid_file_content
#         del self.invalid_file_content
#         codecs.open = self._codecs_open
#         self.parser._create_page = self._create_page
#         self.parser._create_post = self._create_post

#     def test_parse_file(self):
#         """Test that the _parse_file() chooses correct parser
#         for posts and pages
#         """
#         # Mock _create_[post/page] methods
#         self.parser._create_post = mock.Mock(return_value="post")
#         self.parser._create_page = mock.Mock(return_value="page")
#         # Test page
#         self.assertEqual(self.parser._parse_file("path/to/page",
#                                                  "", ""),
#                          "page")
#         # Test post
#         self.assertEqual(self.parser._parse_file("path/to/2013-12-11-blog-post",
#                                                  "", ""),
#                          "post")

#     def test_config_and_content_reader(self):
#         codecs.open = mock.Mock(return_value=CodecsMock(self.valid_file_content))
#         config, content = self.parser._config_and_content_reader("")
#         self.assertEqual(config, {"config": "value",
#                                   "other": 123}
#                          )
#         self.assertEqual(content, u"<p>Body of the file.</p>\n")

#     def test_config_and_content_reader_with_invalid_data(self):
#        codecs.open = mock.Mock(return_value=CodecsMock(self.invalid_file_content))
#        self.assertRaises(MissingYAMLFrontMatterError,
#                          self.parser._config_and_content_reader,
#                          "")
