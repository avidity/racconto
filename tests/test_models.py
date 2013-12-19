import unittest
import datetime

from racconto.models import *

class TestContentBase(unittest.TestCase):

    def setUp(self):
        self.options = {
            "title": "some title",
            "template": "template.jinja",
            "body": "lorem ipsum dolor si amet",
            "filepath": "tests/a-file-name.md",
            "config": ""
            }
        self.content_base = ContentBase(self.options)

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
        other_content_base = ContentBase(other_options)
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


if __name__ == '__main__':
    unittest.main()
