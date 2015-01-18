from datetime import datetime
from functools import total_ordering
from racconto.settings_manager import SettingsManager as SETTINGS

#
# Page containers (Post and Page)
#

class PageFactory(object):
    def page(self, content, info):
        path = info['filepath']
        name = path.split('/')[-1:][0]
        possible_date = " ".join(name.split('-')[0:3])

        try:
            info['date'] = datetime.strptime(possible_date, "%Y %m %d")
            klass = Post
        except ValueError:
            klass = Page

        return klass(content, info)

class PageBase(object):
    """ Base class for compiled content """
    def __init__(self, content, info):
        self.content = content
        self.meta = self.content.meta   # FIXME: Not sure about this interface

        if "slug" in self.meta:
            self.slug = self.meta.slug
        else:
            self.slug = info["filepath"].split("/")[-1:][0].split(".")[0:-1][0]

        if 'title' in self.meta:
            self.title = self.meta.title
        else:
            self.title = "Untitled"

        self.template_parameters = {
            "title": self.title,
            "slug": self.slug,
            "meta": self.meta,
            "content": self.content
        }

    def __str__(self):
        return "%s" % self.title

class Page(PageBase):
    pass
    def __init__(self, content, options):
        super(Page, self).__init__(content, options)
        self.filepath = "%s" % self.slug

        if 'template' in self.meta:
            self.template = self.meta.template
        else:
            self.template = SETTINGS.get('PAGE_TEMPLATE')


@total_ordering # Auto generate missing ordering methods
class Post(PageBase):
    """
    Container for posts
    Implements __lt__ for sorting posts on their published date
    """
    def __init__(self, content, info):
        """
        post - dictionary consisting of post properties
        """
        super(Post, self).__init__(content, info)
        self.slug = self.slug[11:] # Truncate date
        self.date = info['date']

        if 'template' in self.meta:
            self.template = self.meta.template
        else:
            self.template = SETTINGS.get('POST_TEMPLATE')

        self.template_parameters["date"] = self.date
        self.template_parameters["slug"] = self.slug
        self.filepath = "%s/%s" % (
            str(self.date.strftime('%Y-%m-%d')).replace('-','/'),
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

    def __getattr__(self, name):
        try:
            return self.sections[name]
        except KeyError:
            raise AttributeError("No section named %s" % name)

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

class Meta(dict):
    def __init__(self, values={}):
        super(Meta, self).__init__(values)

    def __setitem__(self, key, value):
        raise MetaWriteError("Meta objects are read only")

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("No meta variable %s" % key)

class MetaWriteError(Exception):
    pass
