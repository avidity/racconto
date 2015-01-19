import codecs
import markdown2 as m
import yaml
import re

from racconto.models import *

from racconto.settings_manager import SettingsManager as SETTINGS

class MissingYAMLFrontMatterError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class EndOfFileError(Exception):
    pass

class MetaBlockNotClosedError(Exception):
    pass

class RaccontoParser():
    def __init__(self, filepath):
        self.fh_pos = 0
        self.fh = None
        self.filepath = filepath

        self.re_empty = re.compile(r'^\s*$')
        self.re_meta_marker = re.compile(r'^---\s*$')
        self.re_section_marker = re.compile(r'^\s*@@@\s*(.+)\s*$')

    def parse(self):
        """Parses markdown content to html files.
        If file doesn't have a YAML Front Matter it
        stops parsing and returns None
        """

        page_content = self._parse_file_content()

        return PageFactory().page(page_content, {
            "filepath": self.filepath
        })


    def _parse_file_content(self):
        # FIXME: Open with codecs, but unbuffered
        self.fh = open(self.filepath, 'r', 0) # 'utf-8', 'strict', 0)

        try:
            page_meta = self._meta_section()
            sections  = self._content_sections()
        finally:
            self.fh.close()

        return PageContent(sections, page_meta)


    def _meta_section(self):
        yaml_text = self._parse_meta_section()
        if yaml_text is None:
            return Meta()

        return Meta(yaml.load(yaml_text))

    def _parse_meta_section(self):
        found_marker = False
        yaml = ""

        # Note: the "for line in fh" construct buffers, so we cannot use it while reading by line
        while True:
            line = self.fh.readline()
            if not line:
                break

            if not found_marker:
                if self.re_empty.match(line):
                    pass
                elif self.re_meta_marker.match(line):
                    found_marker = True
                else:
                    # content other than yaml
                    self.fh.seek(self.fh_pos)
                    return None
            else:
                if self.re_meta_marker.match(line):
                    self.fh_pos = self.fh.tell()
                    return yaml

                yaml += line

            self.fh_pos = self.fh.tell()

        raise MetaBlockNotClosedError()


    def _content_sections(self):
        sections = []

        while True:
            try:
                meta = self._meta_section()
                name, content, eof = self._parse_content_section()

                if name is None:
                    name = "section_%s" % len(sections)

                markdown = m.markdown(content, extras=SETTINGS.get('MARKDOWN_EXTRAS'))
                sections.append( Section(name, markdown, meta) )

                if eof:
                    raise EndOfFileError()

            except EndOfFileError:
                break

        return sections


    def _parse_content_section(self):
        found_content = False
        markdown = ""
        name = None

        while True:
            line = self.fh.readline()
            if not line:
                break

            if not found_content:
                if self.re_empty.match(line):
                    continue

                found_content = True

                m = self.re_section_marker.match(line)
                if m:
                    name = m.group(1)
                    continue

            if self.re_section_marker.match(line):
                # rewind line
                self.fh.seek(self.fh_pos)
                return name, markdown, False

            self.fh_pos = self.fh.tell()
            markdown += line

        return name, markdown, True




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
