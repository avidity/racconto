import unittest
import mock
import copy
from datetime import date, timedelta

from racconto.settings_manager import SettingsManager as SETTINGS
from racconto.models import *

# class TestPageBase(unittest.TestCase):
#     def setUp(self):
#         self.options = {
#             "title": "some title",
#             "template": "template.jinja",
#             "body": "lorem ipsum dolor si amet",
#             "filepath": "tests/a-file-name.md",
#             "config": ""
#             }
#         self.content_base = PageBase(self.options)

#     def tearDown(self):
#         del self.content_base

#     def test_populating_variables_from_options_parameter(self):
#         self.assertEqual(self.content_base.title, "some title")
#         self.assertEqual(self.content_base.template, "template.jinja")

#     def test_generated_slug(self):
#         self.assertEqual(self.content_base.slug, "a-file-name")

#     def test_custom_slug(self):
#         other_options = self.options.copy()
#         other_options["slug"] = "my-custom-slug"
#         other_content_base = PageBase(other_options)
#         self.assertEqual(other_content_base.slug, "my-custom-slug")

# class TestPost(unittest.TestCase):
#     def setUp(self):
#         self.options = {
#             "title": "Title of a testing post",
#             "template": "post.jinja",
#             "body": "lorem ipsum dolor si amet",
#             "filepath": "tests/2013-01-01-a-post.md",
#             "config": "",
#             }
#         self.today = datetime.date(2013, 01, 01)

#     def tearDown(self):
#         del self.options

#     def test_posts_can_be_sorted(self):
#         post_list = []
#         # Create a list of posts, each date is one day further in the future
#         for index in range(5):
#             self.options["date"] = self.today + datetime.timedelta(days=index)
#             post = Post(self.options)
#             post_list.append(post)

#         self.assertEqual(len(post_list), 5)
#         self.assertEqual(post_list[0].date, self.today)

#         post_list.sort() # Sorting the list will place the latest post first

#         in_4_days = self.today + datetime.timedelta(days=4)
#         self.assertEqual(post_list[-1].date, self.today)
#         self.assertEqual(post_list[0].date, in_4_days)

class PageFactoryTest(unittest.TestCase):
    def setUp(self):
        self.the_meta = Meta({
            "title": "The page title",
            "slug": "some-slug",
            "template": "a_template"
        })
        self.the_content = PageContent([Section("blah", "some content")], self.the_meta)
        self.the_info = {
            "filepath": "/path/to/a/file.md"
        }
        self.factory = PageFactory()

    def tearDown(self):
        pass

    def test_create_post(self):
        self.the_info['filepath'] = '/path/to/2015-01-18-the-page.md'
        post = self.factory.page(self.the_content, self.the_info)

        self.assertIsInstance(post, Post)

    def test_create_page(self):
        page = self.factory.page(self.the_content, self.the_info)

        self.assertIsInstance(page, Page)

    def test_passes_content(self):
        page = self.factory.page(self.the_content, self.the_info)

        self.assertEqual(page.meta, self.the_meta)
        self.assertEqual(page.content, self.the_content)

class PageTestDefaults(unittest.TestCase):
    def setUp(self):
        self.the_metadata = {
            "title": "The page title",
            "slug": "some-slug",
            "template": "a_template"
        }
        self.the_info = {
            "filepath": "/path/to/a/file.md"
        }
        self.the_content = "Some content"

    def tearDown(self):
        pass

    def content(self):
        return PageContent([Section(self.the_content, Meta())], Meta(self.the_metadata))

    def create_page(self):
        subject = self.subject()
        return subject( self.content(), self.the_info )

class TestPageBase(PageTestDefaults):
    def subject(self):
        return PageBase

    def test_sets_meta_from_content(self):
        page = self.create_page()

        self.assertEqual(page.meta, page.content.meta)

    def test_sets_title_from_meta(self):
        page = self.create_page()

        self.assertEqual(page.title, self.the_metadata['title'])

    def test_title_default(self):
        del self.the_metadata['title']
        page = self.create_page()

        self.assertEqual(page.title, "Untitled")

    def test_sets_slug_from_meta(self):
        page = self.create_page()

        self.assertEqual(page.slug, self.the_metadata['slug'])

    def test_slug_default(self):
        del self.the_metadata['slug']
        page = self.create_page()

        self.assertEqual(page.slug, 'file')

    def test_sets_template_params(self):
        page = self.create_page()

        self.assertEqual(page.template_parameters, {
            "slug": page.slug,
            "meta": page.meta,
            "content": page.content,
            "title": page.title
        })

    def test_stringifies_to_title(self):
        page = self.create_page()

        self.assertEqual("%s" % page, page.title)


class TestPage(PageTestDefaults):
    def subject(self):
        return Page

    def test_sets_template_from_meta(self):
        page = self.create_page()

        self.assertEqual(page.template, self.the_metadata['template'])

    def test_template_default(self):
        del self.the_metadata['template']
        the_template = "my_settings_template"

        # FIXME: Test that the PAGE_TEMPLATE settings is read
        with mock.patch.object(SETTINGS, 'get', return_value=the_template):
            page = self.create_page()
            self.assertEqual(page.template, the_template)


class TestPost(PageTestDefaults):
    def setUp(self):
        super(TestPost, self).setUp()
        #import pdb; pdb.set_trace()
        self.the_info['date'] = date(2015, 01, 18)
        self.the_info['filepath'] = '/path/to/2015-01-18-the-slug.md'

    def subject(self):
        return Post

    def test_sets_template_from_meta(self):
        page = self.create_page()

        self.assertEqual(page.template, self.the_metadata['template'])

    def test_template_default(self):
        del self.the_metadata['template']
        the_template = "my_settings_template"

        # FIXME: Test that the POST_TEMPLATE settings is read
        with mock.patch.object(SETTINGS, 'get', return_value=the_template):
            page = self.create_page()
            self.assertEqual(page.template, the_template)

    def test_slug_value(self):
        del self.the_metadata['slug']
        page = self.create_page()
        self.assertEqual(page.slug, 'the-slug')

    def test_date_property(self):
        page = self.create_page()
        self.assertEqual(page.date, self.the_info['date'])

    def test_file_path(self):
        page = self.create_page()
        self.assertEqual(page.filepath, '2015/01/18/some-slug')

    def test_file_path_no_meta_slug(self):
        del self.the_metadata['slug']
        page = self.create_page()
        self.assertEqual(page.filepath, '2015/01/18/the-slug')

    def test_posts_can_be_sorted(self):
        post_list = []
        today = date(2015, 01, 18)

        for index in range(5):
            self.the_info['date'] = today + timedelta(days=index)
            post_list.append( Post(self.content(), self.the_info) )

        post_list.sort()
        in_4_days = today + timedelta(days=4)
        self.assertEqual(post_list[-1].date, today)
        self.assertEqual(post_list[0].date, in_4_days)


class TestSection(unittest.TestCase):
    def setUp(self):
        self.the_content = "This is the content"
        self.the_name = "my section"

        self.section = Section(self.the_name, self.the_content)

    def tearDown(self):
        pass

    def test_name_option(self):
        self.assertEqual(self.section.name, self.the_name)

    def test_content_option(self):
        self.assertEqual(self.section.content, self.the_content)

    def test_stringifies_to_content(self):
        self.assertEqual("%s" % (self.section), self.the_content)

class TestMeta(unittest.TestCase):
    def setUp(self):
        self.the_metadata = {
            "title": "The Homepage",
            "author": "Gunnar Hansson"
        }
        self.meta = Meta(self.the_metadata)

    def tearDown(self):
        pass

    def test_meta_is_a_dictionary(self):
        self.assertIsInstance(self.meta, dict)

    def test_access_variables_as_property(self):
        self.assertEqual(self.meta.title, self.the_metadata['title'])

    def test_empty_meta(self):
        self.assertEqual(Meta(), {})

class TestPageContent(unittest.TestCase):
    def setUp(self):
        self.the_meta = Meta({})
        self.the_sections = [
            Section("section_1", "This is section 1"),
            Section("section_2", "This movie is stupid")
        ]

        self.page_content = PageContent(self.the_sections, self.the_meta)

    def tearDown(self):
        pass

    def test_iterate_sections(self):
        s = iter(self.the_sections)
        for section in self.page_content:
            self.assertEqual(section, next(s))

    def test_sections_length(self):
        self.assertEqual(len(self.page_content), 2)

    def test_sections_is_dict_keyed_on_name(self):
        self.assertEqual(self.page_content.sections['section_1'], self.the_sections[0])
        self.assertEqual(self.page_content.sections['section_2'], self.the_sections[1])

    def test_meta_property(self):
        self.assertEqual(self.page_content.meta, self.the_meta)

    def test_access_section_on_name(self):
        self.assertEqual(self.page_content.section_1, self.the_sections[0])

    def test_stringifies_to_all_content(self):
        self.assertEqual("%s" % self.page_content, "This is section 1\nThis movie is stupid")


if __name__ == '__main__':
    unittest.main()

