# -*- coding: utf-8 -*-
# Written by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026,
# as part of MoinMoin 1.11.0+md1 (Markdown support).
"""
    MoinMoin - Markdown parser

    Renders pages written in Markdown. A page without a #format line is
    recognized as Markdown from its text (cfg.markup_autodetect, see
    wikiutil.detect_markup); "#format markdown" in the first lines forces
    it. Markdown and native MoinMoin wiki pages can be mixed freely in the
    same wiki.

    The rendering is done by the Python-Markdown library; the parts that
    need the wiki are given to the MoinMoin formatter, so they work like in
    wiki markup pages (page cache, backlinks, LocalSiteMap, TableOfContents,
    syntax highlighting, ...):

     * [[PageName]], [[PageName|text]], [[PageName#anchor|text]]  wiki links
     * [[WikiName:PageName]], [[attachment:file.pdf|text]]          interwiki / attachment links
     * [text](PageName), [text](../SisterPage), [text](/SubPage)  links to wiki pages
     * [text](attachment:file.pdf), ![alt](attachment:image.png)   attachments
     * [text](https://example.org)                                 external links
     * <<MacroName(arguments)>>                                    MoinMoin macros
     * ```python ... ```                                           highlighted code
     * ```wiki / creole / rst / csv ... ```                        blocks in another markup
     * # / ## / ### headings                                       (also used by <<TableOfContents>>)

    Raw HTML is not rendered (it is shown as text) and only safe URL schemes
    are allowed in links, so Markdown pages cannot inject scripts.

    @license: GNU GPL, see COPYING for details.
"""

import copy
import re
import xml.etree.ElementTree as etree

import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor
from markdown.serializers import to_html_string

from MoinMoin import log
logging = log.getLogger(__name__)

from MoinMoin import wikiutil
from MoinMoin import macro as wikimacro

Dependencies = []

# placeholders for the parts rendered by the MoinMoin formatter
# (private use unicode characters: they pass unchanged through markdown)
PH_START, PH_END = '', ''
PH_RE = re.compile(PH_START + r'(\d+)' + PH_END)
BLOCK_PH_RE = re.compile(r'<p>\s*(' + PH_START + r'\d+' + PH_END + r')\s*</p>')
PH_TAG = 'moinph'

# URL schemes allowed in links and images (javascript:, data:, vbscript:, ...
# are not)
SAFE_SCHEMES = ('http', 'https', 'ftp', 'ftps', 'sftp', 'mailto', 'news', 'nntp',
                'irc', 'ircs', 'xmpp', 'tel', 'gopher', 'ssh', 'git', 'svn', 'file')
SCHEME_RE = re.compile(r'^([A-Za-z][A-Za-z0-9+.\-]*):(.*)$', re.S)

# fenced blocks with these names are rendered with that MoinMoin parser
# (all the other names are languages for the syntax highlighting)
MARKUP_BLOCKS = {'wiki': 'wiki', 'moin': 'wiki', 'creole': 'creole', 'rst': 'rst', 'csv': 'csv', }

# Python-Markdown extensions used by default (wiki config: markdown_extensions)
DEFAULT_EXTENSIONS = ['tables', 'footnotes', 'def_list', 'abbr', 'sane_lists']


class _Store(object):
    """ the parts that are rendered later by the MoinMoin formatter """
    def __init__(self):
        self.items = []

    def add(self, kind, **data):
        data['kind'] = kind
        self.items.append(data)
        return '%s%d%s' % (PH_START, len(self.items) - 1, PH_END)


class FencedCodePreprocessor(Preprocessor):
    """ ```lang ... ``` and ~~~lang ... ~~~ blocks (before markdown sees them) """
    FENCE_RE = re.compile(r'^(?P<indent>[ ]{0,3})(?P<fence>`{3,}|~{3,})[ \t]*(?P<lang>[\w+#.\-]*)[^`]*$')

    def __init__(self, md, store):
        Preprocessor.__init__(self, md)
        self.store = store

    def run(self, lines):
        out = []
        i = 0
        while i < len(lines):
            m = self.FENCE_RE.match(lines[i])
            if not m:
                out.append(lines[i])
                i += 1
                continue
            fence = m.group('fence')
            lang = m.group('lang')
            code = []
            j = i + 1
            while j < len(lines):
                stripped = lines[j].strip()
                if stripped.startswith(fence[0] * len(fence)) and set(stripped) == set(fence[0]):
                    break
                code.append(lines[j])
                j += 1
            ph = self.store.add('code', lang=lang, lines=code)
            out.extend(['', ph, ''])
            i = j + 1
        return out


class WikiLinkProcessor(InlineProcessor):
    """ [[target]], [[target|label]] like in MoinMoin wiki markup """
    def __init__(self, pattern, md, parser):
        InlineProcessor.__init__(self, pattern, md)
        self.parser = parser

    def handleMatch(self, m, data):
        target = m.group(1).strip()
        label = m.group(2)
        label_html = wikiutil.escape(label.strip()) if label is not None else None
        return self.parser.link_placeholder(target, label_html), m.start(0), m.end(0)


class MacroProcessor(InlineProcessor):
    """ <<MacroName(args)>> like in MoinMoin wiki markup """
    def __init__(self, pattern, md, store):
        InlineProcessor.__init__(self, pattern, md)
        self.store = store

    def handleMatch(self, m, data):
        return (self.store.add('macro', name=m.group(1), args=m.group(2), markup=m.group(0)),
                m.start(0), m.end(0))


class MoinTreeprocessor(Treeprocessor):
    """ hand links, images, headings over to the MoinMoin formatter """
    def __init__(self, md, parser):
        Treeprocessor.__init__(self, md)
        self.parser = parser

    def _inner_html(self, el):
        """ html of the content of el (el is not modified) """
        div = copy.deepcopy(el)
        div.tag = 'div'
        div.attrib.clear()
        div.tail = None
        html = to_html_string(div)
        return html[len('<div>'):-len('</div>')]

    def _replace(self, el, placeholder):
        tail = el.tail
        el.clear()
        el.tag = PH_TAG
        el.text = placeholder
        el.tail = tail

    def run(self, root):
        for el in list(root.iter()):
            if el.tag == 'a':
                href = el.get('href', '')
                if href.startswith('#') and 'class' not in el.attrib:
                    continue # anchor in this page (also footnotes)
                if el.get('class') in ('footnote-ref', 'footnote-backref'):
                    continue
                ph = self.parser.link_placeholder(href, self._inner_html(el) or None)
                if ph is not None: # wiki page, attachment, interwiki, ...
                    self._replace(el, ph)
            elif el.tag == 'img':
                ph = self.parser.image_placeholder(el.get('src', ''), el.get('alt', ''), el.get('title'))
                if ph is not None:
                    self._replace(el, ph)
            elif el.tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                text = ''.join(el.itertext()).strip()
                ph = self.parser.store.add('heading', level=int(el.tag[1]), text=text,
                                           html=self._inner_html(el))
                self._replace(el, ph)


class MoinExtension(Extension):
    def __init__(self, parser):
        Extension.__init__(self)
        self.parser = parser

    def extendMarkdown(self, md):
        store = self.parser.store
        # no raw HTML: it is escaped and shown as text
        md.preprocessors.deregister('html_block')
        md.inlinePatterns.deregister('html')
        md.preprocessors.register(FencedCodePreprocessor(md, store), 'moin_fenced_code', 28)
        # higher priority than links, lower than `code spans` (190)
        md.inlinePatterns.register(
            WikiLinkProcessor(r'\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]', md, self.parser), 'moin_wikilink', 175)
        md.inlinePatterns.register(
            MacroProcessor(r'<<([A-Za-z_][A-Za-z0-9_]*)(?:\((.*?)\))?>>', md, store), 'moin_macro', 174)
        # runs after all markdown tree processors (also after "unescape")
        md.treeprocessors.register(MoinTreeprocessor(md, self.parser), 'moin_tree', -10)


class Parser:
    """ Markdown parser """

    extensions = ['.md', '.markdown', ]
    caching = 1
    Dependencies = Dependencies

    def __init__(self, raw, request, **kw):
        self.raw = raw
        self.request = request
        self.form = request.form
        self._ = request.getText
        self.store = _Store()
        self.macro = None
        self.formatter = None
        self.pagename = ''

    # the placeholder factories -------------------------------------------

    def link_placeholder(self, target, label_html):
        """ placeholder for a link to target, or None for links that markdown
            renders itself (external URLs, anchors)
        """
        target = target.strip()
        if not target:
            return None
        if target.startswith('#'):
            return None
        m = SCHEME_RE.match(target)
        if m:
            scheme, rest = m.group(1), m.group(2)
            if scheme.lower() in SAFE_SCHEMES:
                return None
            if scheme == 'attachment':
                return self.store.add('attachment_link', url=rest, label=label_html)
            if self._is_interwiki(scheme):
                return self.store.add('interwiki', wiki=scheme, page=rest, label=label_html)
            # unknown or dangerous scheme (javascript:, data:, ...): just text
            return self.store.add('text', text=target, label=label_html)
        pagename, anchor = wikiutil.split_anchor(target)
        return self.store.add('page', page=pagename, anchor=anchor, label=label_html,
                              markup=target)

    def image_placeholder(self, src, alt, title):
        src = src.strip()
        m = SCHEME_RE.match(src)
        if m:
            scheme, rest = m.group(1), m.group(2)
            if scheme.lower() in ('http', 'https', 'ftp', 'ftps'):
                return None # external image
            if scheme == 'attachment':
                return self.store.add('attachment_image', url=rest, alt=alt, title=title)
            return self.store.add('text', text=alt or src, label=None)
        # no scheme: an attachment of this (or another) page
        return self.store.add('attachment_image', url=src, alt=alt, title=title)

    def _is_interwiki(self, name):
        try:
            return not wikiutil.resolve_interwiki(self.request, name, '')[3]
        except Exception:
            return False

    # rendering -------------------------------------------------------------

    def _markdown(self):
        cfg = self.request.cfg
        extensions = list(getattr(cfg, 'markdown_extensions', None) or DEFAULT_EXTENSIONS)
        extensions.append(MoinExtension(self))
        return markdown.Markdown(extensions=extensions, output_format='html')

    def format(self, formatter, **kw):
        """ Send the text. """
        self.formatter = formatter
        self.pagename = formatter.page.page_name
        md = self._markdown()
        html = md.convert(self.raw)
        html = html.replace('<%s>' % PH_TAG, '').replace('</%s>' % PH_TAG, '')
        html = BLOCK_PH_RE.sub(r'\1', html)

        def postprocess(s):
            # labels were serialized before the markdown postprocessors ran
            for pp in md.postprocessors:
                s = pp.run(s)
            return s

        write = self.request.write
        pos = 0
        write(formatter.div(1, css_class='markdown'))
        for m in PH_RE.finditer(html):
            write(formatter.rawHTML(html[pos:m.start()]))
            write(self._render(self.store.items[int(m.group(1))], postprocess))
            pos = m.end()
        write(formatter.rawHTML(html[pos:]))
        write(formatter.div(0))

    def _label(self, item, default, postprocess):
        f = self.formatter
        if item.get('label'):
            return f.rawHTML(postprocess(item['label']))
        return f.text(default)

    def _render(self, item, postprocess):
        f = self.formatter
        kind = item['kind']
        if kind == 'page':
            page = item['page']
            if not page: # [text](#anchor) is handled by markdown, [[#anchor]] here
                return (f.anchorlink(1, item['anchor']) + self._label(item, item['markup'], postprocess) +
                        f.anchorlink(0))
            pagename = wikiutil.AbsPageName(self.pagename, page)
            return (f.pagelink(1, pagename, anchor=item['anchor']) +
                    self._label(item, item['markup'], postprocess) +
                    f.pagelink(0, pagename))
        elif kind == 'interwiki':
            page, anchor = wikiutil.split_anchor(item['page'])
            return (f.interwikilink(1, item['wiki'], page, anchor=anchor) +
                    self._label(item, '%s:%s' % (item['wiki'], item['page']), postprocess) +
                    f.interwikilink(0, item['wiki'], page))
        elif kind == 'attachment_link':
            return (f.attachment_link(1, item['url']) +
                    self._label(item, item['url'], postprocess) +
                    f.attachment_link(0))
        elif kind == 'attachment_image':
            kw = {'alt': item['alt'] or item['url']}
            if item.get('title'):
                kw['title'] = item['title']
            return f.attachment_image(item['url'], **kw)
        elif kind == 'macro':
            if self.macro is None:
                self.macro = wikimacro.Macro(self)
            return f.macro(self.macro, item['name'], item['args'], markup=item['markup'])
        elif kind == 'heading':
            level = item['level']
            return (f.heading(1, level, id=item['text']) +
                    f.rawHTML(postprocess(item['html'])) +
                    f.heading(0, level))
        elif kind == 'code':
            # formatter.parser() writes its output, but the caching formatter
            # returns a marker for the code it generated: it must be written
            return self._code(item['lang'], item['lines'])
        elif kind == 'text':
            return self._label(item, item['text'], postprocess)
        return ''

    def _code(self, lang, lines):
        """ fenced code: a MoinMoin parser of that name (wiki, creole, rst,
            csv, ...) or syntax highlighting of that language
        """
        f = self.formatter
        lang = (lang or '').strip()
        if not lang:
            return f.parser('text', lines) or ''
        markup = MARKUP_BLOCKS.get(lang.lower())
        if markup:
            return f.parser(markup, ['#!%s' % markup] + list(lines)) or ''
        return f.parser('highlight', ['#!highlight %s' % lang] + list(lines)) or ''
