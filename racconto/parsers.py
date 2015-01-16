import codecs
from datetime import datetime
import markdown2 as m
import yaml
import re

from racconto.models import Post, Page

from racconto.settings_manager import SettingsManager as SETTINGS

class MissingYAMLFrontMatterError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class EndOfFileError(Exception):
    pass

class MetaBlockNotClosedError(EndOfFileError):
    pass

class RaccontoParser():
    def __init__(self):

        self.re_empty = re.compile(r'^\s*$')
        self.re_meta_marker = re.compile(r'^---$')
        self.re_section_marker = re.compile(r'^\s*@@@\s*(.+)\s*$')

    def parse(self, filepath):
        """Parses markdown content to html files.
        If file doesn't have a YAML Front Matter it
        stops parsing and returns None
        """
        try:
            page_meta, sections = self._parse_file_content(filepath)
            #config, content = self._config_and_content_reader(filepath)
        except MissingYAMLFrontMatterError:
            print "File at '%s' is missing a YAML Front Matter config" % filepath
            return None

        return self._parse_file(filepath, config, content)


    def _parse_file_content(self, filepath):
        sections = []

        fh = codecs.open(filepath, 'r', 'utf-8')
        try:
            page_meta = self._meta_section(self, fh)
            sections  = self._content_sections(self, fh)

        finally:
            fh.close()


        return page_meta, sections


    def _meta_section(self, fh):
        yaml = self._parse_meta_section(fh)
        if yaml is None:
            return None

        return Meta({})
        # Parse YAML, create Meta object and return

    def _parse_meta_section(self, fh):
        found_marker = False
        yaml = ""

        while line in fh.readline():
            if not found_marker:
                if line.match(self.re_empty):
                    continue
                elif line.match(self.re_meta_marker):
                    found_marker = True
                    continue
                else:
                    # content other than yaml
                    # FIXME: rewind one line
                    return None
            else:
                if line.match(self.re_meta_marker):
                    return yaml

                yaml += line

        raise MetaBlockNotClosedError()


    def _content_sections(self, fh):
        sections = []
        while True:
            try:
                meta = self._meta_section(fh)
                name, markdown = self._parse_content_section(fh)
            except EndOfFileError:
                break

            if name is None:
                name = "section-%s" % len(sections)

            # FIXME: Parse markdown here
            sections.append( Section(name, markdown, meta) )

        return sections


    def _parse_content_section(self, fh):
        has_marker = False
        markdown = ""

        while line in fh.readline():
            pass

        raise EndOfFileError()


    # def _config_and_content_reader(self, filepath):
    #     """Reads config and content from file """
    #     config_separator = SETTINGS.get('CONFIG_SEPARATOR')
    #     f = codecs.open(filepath, 'r', 'utf-8')
    #     lines = f.readlines()
    #     f.close()

    #     raw_data = {"config": "", "content": "", "reading_config": False }

    #     for index, line in enumerate(lines):
    #         # File must start with YAML Front Matter
    #         if index == 0 and not line.startswith(config_separator):
    #             raise MissingYAMLFrontMatterError("File must start with YAML Front Matter")

    #         if line.startswith(config_separator):
    #             raw_data["reading_config"] = not raw_data["reading_config"]
    #             continue
    #         if raw_data["reading_config"]:
    #             raw_data["config"] += line
    #         else:
    #             raw_data["content"] += line

    #     if raw_data["reading_config"]:
    #       raise MissingYAMLFrontMatterError("Reached EOF before YAML Front Matter ended")

    #     # Parse config and content
    #     config = yaml.load(raw_data["config"])
    #     extras = SETTINGS.get('MARKDOWN_EXTRAS')
    #     content = m.markdown(raw_data["content"], extras=extras)

    #     return config, content

    # def _parse_file(self, filepath, config, content):
    #     """Determines what type of content this is from filename
    #     and then calls the appropriate object creator method
    #     """
    #     filename = filepath.split('/')[-1:][0]
    #     possible_date = " ".join(filename.split('-')[0:3])
    #     try:
    #         date = datetime.strptime(possible_date, "%Y %m %d")
    #         return self._create_post(filepath, config, content, date)
    #     except ValueError:
    #         return self._create_page(filepath, config, content)

    # def _create_post(self, filepath, config, content, date):
    #     """Creates a Post from file data
    #     """
    #     template = config.get("template", SETTINGS.get('POST_TEMPLATE'))
    #     return Post({
    #             "title": config["title"],
    #             "body":  content,
    #             "template": template,
    #             "date": date,
    #             "filepath": filepath,
    #             "config": config,
    #             })

    # def _create_page(self, filepath, config, content):
    #     """Creates a Page from file data
    #     """
    #     template = config.get("template", SETTINGS.get('PAGE_TEMPLATE'))
    #     return Page({
    #             "title": config["title"],
    #             "body": content,
    #             "template": template,
    #             "filepath": filepath,
    #             "config": config,
    #             })
