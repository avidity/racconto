import codecs
import markdown2 as m
import yaml
import re

from racconto.models import *

from racconto.settings_manager import SettingsManager as SETTINGS

class RaccontoParserError(Exception):
    pass

class EndOfFileError(RaccontoParserError):
    pass

class MetaBlockNotClosedError(RaccontoParserError):
    pass

class MetaBlockYAMLParseError(RaccontoParserError):
    def __init__(self, ex):
        self.value = "%s" % ex

    def __str__(self):
        return repr(self.value)

class SectionNameError(RaccontoParserError):
    def __init__(self, name):
        self.value = "%s not not a valid section name ([a-z0-9_]+)" % name


class RaccontoParser():
    def __init__(self, filepath):
        self.fh_pos = 0
        self.fh = None
        self.filepath = filepath

        self.re_empty = re.compile(r'^\s*$')
        self.re_meta_marker = re.compile(r'^---\s*$')
        self.re_section_marker = re.compile(r'^\s*@@@\s*(?:(.+))?\s*$')
        self.re_section_name = re.compile(r'^[a-z0-9_]+$', re.IGNORECASE)

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

        try:
            return Meta(yaml.load(yaml_text))
        except yaml.YAMLError, ex:
            raise MetaBlockYAMLParseError(ex)

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
                name, meta, content, eof = self._parse_content_section()

                if name is None:
                    name = "section_%s" % len(sections)
                elif not self.re_section_name.match(name):
                    raise SectionNameError(name)

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
        meta = None
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
                    meta = self._meta_section()

                    # Here's an ugly fix. We discovered no meta, but something
                    # else. The _meta_section() code then rolls back to the
                    # previous line, but we've just parsed it. So, we roll it
                    # forward again.
                    if len(meta) == 0:
                        self.fh.readline()

                    continue

            if self.re_section_marker.match(line):
                # rewind line
                self.fh.seek(self.fh_pos)
                return name, meta, markdown, False

            self.fh_pos = self.fh.tell()
            markdown += line

        return name, meta, markdown, True
