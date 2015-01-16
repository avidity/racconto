import unittest
import datetime
import copy

from racconto.models import *

class TestPageBase(unittest.TestCase):
    def setUp(self):
        self.options = {
            "title": "some title",
            "template": "template.jinja",
            "body": "lorem ipsum dolor si amet",
            "filepath": "tests/a-file-name.md",
            "config": ""
            }
        self.content_base = PageBase(self.options)

    def tearDown(self):
        del self.content_base

    def test_populating_variables_from_options_parameter(self):
        self.assertEqual(self.content_base.title, "some title")
        self.assertEqual(self.content_base.template, "template.jinja")

    def test_generated_slug(self):
        self.assertEqual(self.content_base.slug, "a-file-name")

    def test_custom_slug(self):
        other_options = self.options.copy()
        other_options["slug"] = "my-custom-slug"
        other_content_base = PageBase(other_options)
        self.assertEqual(other_content_base.slug, "my-custom-slug")

class TestPost(unittest.TestCase):
    def setUp(self):
        self.options = {
            "title": "Title of a testing post",
            "template": "post.jinja",
            "body": "lorem ipsum dolor si amet",
            "filepath": "tests/2013-01-01-a-post.md",
            "config": "",
            }
        self.today = datetime.date(2013, 01, 01)

    def tearDown(self):
        del self.options

    def test_posts_can_be_sorted(self):
        post_list = []
        # Create a list of posts, each date is one day further in the future
        for index in range(5):
            self.options["date"] = self.today + datetime.timedelta(days=index)
            post = Post(self.options)
            post_list.append(post)

        self.assertEqual(len(post_list), 5)
        self.assertEqual(post_list[0].date, self.today)

        post_list.sort() # Sorting the list will place the latest post first

        in_4_days = self.today + datetime.timedelta(days=4)
        self.assertEqual(post_list[-1].date, self.today)
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

class TestPageContent(unittest.TestCase):
    def setUp(self):
        self.the_meta = Meta({})
        self.the_sections = [
            Section("section-1", "This is section 1"),
            Section("section-2", "This movie is stupid")
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
        self.assertEqual(self.page_content.sections['section-1'], self.the_sections[0])
        self.assertEqual(self.page_content.sections['section-2'], self.the_sections[1])

    def test_meta_property(self):
        self.assertEqual(self.page_content.meta, self.the_meta)


if __name__ == '__main__':
    unittest.main()

