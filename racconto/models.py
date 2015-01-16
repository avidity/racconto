import datetime
from functools import total_ordering
from racconto.settings_manager import SettingsManager as SETTINGS

#
# Page containers (Post and Page)
#

class PageBase(object):
    """ Base class for compiled content """
    def __init__(self, options):
        self.title = options["title"]
        self.template = options["template"]
        self.content = PageContent(options["content"], options["meta"])
        self.meta = self.content.meta   # FIXME: Not sure about this interface

        if "slug" in options.keys():
            self.slug = options["slug"]
        else:
            self.slug = options["filepath"].split("/")[-1:][0].split(".")[0:-1][0]

        self.template_parameters = {"title": self.title,
                                    "content": self.content
                                   }
        # Add config variables to template parameters
        for param in options["config"]:
            self.template_parameters[param] = options["config"][param]

class Page(PageBase):
    def __init__(self, options):
        super(Page, self).__init__(options)
        self.filepath = "%s" % self.slug
        self.template = options["config"].get("template", SETTINGS.get('PAGE_TEMPLATE'))

    def __str__(self):
        return "%s" % self.title


@total_ordering # Auto generate missing ordering methods
class Post(PageBase):
    """
    Container for posts
    Implements __lt__ for sorting posts on their published date
    """
    def __init__(self, options):
        """
        post - dictionary consisting of post properties
        """
        super(Post, self).__init__(options)
        self.slug = self.slug[11:] # Truncate date
        self.date = options["date"]
        # FIXME: Fix this
        self.template = options["template"] # , SETTINGS.get('PAGE_TEMPLATE'))
        self.template_parameters["date"] = self.date
        self.filepath = "%s/%s" % (str(self.date.strftime('%Y-%m-%d')).replace('-','/'),
            self.slug,
            )

    def __repr__(self):
        return "Post('%s', %s)" % (self.title, self.date)

    def __str__(self):
        return "%s (%s)" % (self.title, self.date)

    def __eq__(self, other):
        return self.date == other.date

    def __lt__(self, other):
        return self.date > other.date



#
# Content containers (Meta and Section)
#

class PageContent(object):
    def __init__(self, sections, page_meta=None):
        self._iter_sections = iter(sections)
        self.sections = dict((s.name, s) for s in sections)
        self.meta = page_meta

    def next(self):
        next(self._iter_sections)

    def __iter__(self):
        return self._iter_sections

    def __len__(self):
        return len(self.sections)

    def __str__(self):
        return "\n".join(self.sections)


class Section(object):
    def __init__(self, name, content, meta=None):
        self.name = name
        self.meta = meta
        self.content = content

    def __repr__(self):
        return "Section('%s')" % (self.name)

    def __str__(self):
        return "%s" % (self.content)

class Meta(object):
    def __init__(self, options):
        self.options = options
