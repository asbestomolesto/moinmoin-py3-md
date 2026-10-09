# -*- coding: utf-8 -*-
# Written by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026,
# as part of MoinMoin 1.11.0+md1 (Markdown support).
"""
    MoinMoin - MoinMoin.parser.text_markdown Tests

    @license: GNU GPL, see COPYING for details.
"""

import re

import pytest

from MoinMoin.Page import Page
from MoinMoin.parser.text_markdown import Parser as MarkdownParser
from MoinMoin.formatter.text_html import Formatter as HtmlFormatter
from MoinMoin.formatter.pagelinks import Formatter as PageLinksFormatter
from MoinMoin import wikiutil

PAGENAME = 'MarkdownParserTestPage'


class ParserTestCase(object):
    """ Helper class that provides a parsing method """

    def parse(self, body, formatter_class=HtmlFormatter, **formatter_kw):
        request = self.request
        request.reset()
        page = Page(request, PAGENAME)
        page.hilite_re = None
        page.set_raw_body('#format markdown\n' + body)
        formatter = formatter_class(request, **formatter_kw)
        formatter.setPage(page)
        page.formatter = formatter
        request.formatter = formatter
        request.page = page
        parser = MarkdownParser(body, request)
        formatter.startContent('')
        output = request.redirectedOutput(parser.format, formatter)
        formatter.endContent('')
        return output


class TestBasics(ParserTestCase):

    def test_paragraph_and_emphasis(self):
        result = self.parse('Some **bold** and *italic* text.')
        assert '<strong>bold</strong>' in result
        assert '<em>italic</em>' in result
        assert re.search(r'<p>\s*Some', result)

    def test_headings_go_through_formatter(self):
        result = self.parse('# Title\n\n## Section two\n')
        assert re.search(r'<h1 id="Title">\s*Title\s*</h1>', result)
        assert re.search(r'<h2 id="Section_two">\s*Section two\s*</h2>', result)

    def test_heading_with_markup(self):
        result = self.parse('## A *nice* heading\n')
        assert re.search(r'<h2 id="A_nice_heading">\s*A <em>nice</em> heading\s*</h2>', result)

    def test_table(self):
        result = self.parse('| a | b |\n|---|---|\n| 1 | 2 |\n')
        assert '<table>' in result
        assert '<td>2</td>' in result

    def test_footnote(self):
        result = self.parse('Text[^1].\n\n[^1]: The note.\n')
        assert 'class="footnote-ref"' in result
        assert 'The note.' in result


class TestLinks(ParserTestCase):

    def test_wikilink(self):
        result = self.parse('See [[FrontPage]].')
        assert re.search(r'<a href="[^"]*/FrontPage">FrontPage</a>', result)

    def test_wikilink_with_label_and_anchor(self):
        result = self.parse('[[FrontPage#here|the front]]')
        assert re.search(r'<a href="[^"]*/FrontPage#here">the front</a>', result)

    def test_nonexistent_page(self):
        result = self.parse('[[ThisPageDoesNotExistAtAll]]')
        assert 'class="nonexistent"' in result

    def test_markdown_link_to_page(self):
        result = self.parse('[the front](FrontPage)')
        assert re.search(r'<a href="[^"]*/FrontPage">the front</a>', result)

    def test_markdown_link_keeps_label_markup(self):
        result = self.parse('[*the* front](FrontPage)')
        assert re.search(r'<a href="[^"]*/FrontPage"><em>the</em> front</a>', result)

    def test_subpage_link(self):
        result = self.parse('[sub](/Sub)')
        assert '/%s/Sub' % PAGENAME in result

    def test_external_link(self):
        result = self.parse('[Python](https://www.python.org)')
        assert '<a href="https://www.python.org">Python</a>' in result

    def test_interwiki(self):
        result = self.parse('[[MoinMoin:FrontPage]]')
        assert 'class="interwiki"' in result

    def test_attachment_link(self):
        result = self.parse('[[attachment:doc.pdf|the doc]]')
        assert 'do=upload_form' in result and 'target=doc.pdf' in result
        assert 'the doc' in result

    def test_attachment_image(self):
        result = self.parse('![logo](attachment:logo.png)')
        assert 'target=logo.png' in result

    def test_dangerous_links_are_not_links(self):
        result = self.parse('[click](javascript:alert(1)) ![x](data:image/png;base64,AAA)')
        assert 'javascript:' not in result
        assert 'data:image' not in result
        assert 'click' in result

    def test_pagelinks_are_collected(self):
        result = self.parse('[[FrontPage]] [x](HelpContents) [y](https://example.org)',
                            formatter_class=PageLinksFormatter, store_pagelinks=1)
        links = self.request.formatter.pagelinks
        assert 'FrontPage' in links
        assert 'HelpContents' in links
        assert len(links) == 2


class TestMacrosAndCode(ParserTestCase):

    def test_macro(self):
        result = self.parse('Today: <<Date(2026-10-09T10:00:00)>>')
        assert '2026-10-09' in result
        assert '&lt;&lt;' not in result

    def test_macro_not_in_code_span(self):
        result = self.parse('`<<Date>>`')
        assert '<code>&lt;&lt;Date&gt;&gt;</code>' in result

    def test_fenced_code_highlighted(self):
        result = self.parse('```python\ndef f():\n    return 1\n```\n')
        assert 'class="highlight python"' in result
        assert '<span class="ResWord">def</span>' in result

    def test_fenced_code_without_language(self):
        result = self.parse('```\n<b>x</b>\n```\n')
        assert '&lt;b&gt;x&lt;/b&gt;' in result
        assert '<b>x</b>' not in result

    def test_fenced_wiki_block(self):
        result = self.parse("```wiki\n'''bold''' [[FrontPage]]\n```\n")
        assert '<strong>bold</strong>' in result
        assert re.search(r'<a href="[^"]*/FrontPage">', result)

    def test_no_raw_html(self):
        result = self.parse('<script>alert(1)</script>\n\n<b onclick="x()">t</b>')
        assert '<script>' not in result
        assert 'onclick="x()"' not in result or '&lt;b onclick' in result
        assert '&lt;script&gt;' in result


class TestPageCache(object):
    """ the page cache stores the output as python code (text_python
        formatter): it must give the same result as the direct rendering
    """
    text = """#format markdown
# Title

<<TableOfContents>>

## Code

```python
print("hello")
```

```
plain
```

```wiki
'''bold''' [[FrontPage]]
```

## Macro

Pages: <<PageCount>> and [[FrontPage|a link]] ![img](attachment:x.png)
"""

    def render(self, request, use_cache):
        from MoinMoin.formatter.text_html import Formatter
        request.reset()
        request.cfg.cfg_mtime = 1 # allow the cached code to run
        page = Page(request, PAGENAME)
        page.set_raw_body(self.text)
        page.hilite_re = None
        formatter = Formatter(request)
        formatter.setPage(page)
        page.formatter = formatter
        request.formatter = formatter
        request.page = page
        parser = MarkdownParser(page.data, request)
        formatter.startContent('')
        if use_cache:
            code = page.makeCache(request, parser)
            output = request.redirectedOutput(page.execute, request, parser, code)
        else:
            output = request.redirectedOutput(parser.format, formatter)
        formatter.endContent('')
        output = re.sub(r'ticket=[0-9a-f.]+|CA-[0-9a-f]+', 'X', output)
        # ids are made unique per request, the second rendering gets other ones
        return re.sub(r'(id="|href="#)[^"]*"', r'\1X"', output)

    def test_cached_output_is_the_same(self):
        direct = self.render(self.request, False)
        cached = self.render(self.request, True)
        assert 'Pages: ' in direct and '<strong>bold</strong>' in direct
        assert direct == cached


class TestProcessingInstructions(object):

    def test_markdown_heading_is_not_a_pi(self):
        pi, body = wikiutil.get_processing_instructions('#format markdown\n# Title\ntext\n')
        assert pi == [('format', 'markdown')]
        assert body == '# Title\ntext\n'

    def test_markdown_h2_is_not_a_comment(self):
        pi, body = wikiutil.get_processing_instructions('#format markdown\n## Section\n')
        assert body == '## Section\n'

    def test_moin_comments_stay_comments(self):
        text = '## page was renamed from OldName\n#format markdown\n## Section\n'
        pi, body = wikiutil.get_processing_instructions(text)
        assert pi[0] == ('#', 'page was renamed from OldName')
        assert body == '## Section\n'

    def test_wiki_comments_unchanged(self):
        pi, body = wikiutil.get_processing_instructions('#format wiki\n## a comment\n= T =\n')
        assert ('#', 'a comment') in pi
        assert body == '= T =\n'

    def test_default_markup_markdown(self):
        pi, body = wikiutil.get_processing_instructions('# Title\n', 'markdown')
        assert pi == [] and body == '# Title\n'

    def test_format_name_finds_parser(self):
        from MoinMoin.parser import text_markdown
        mt = wikiutil.MimeType('markdown')
        assert 'text_markdown' in list(mt.module_name())


class TestDetectMarkup(object):
    """ pages without a #format line: the markup is guessed from the text """

    def test_markdown(self):
        text = '# Title\n\nSome **bold** text and [a link](FrontPage).\n\n- one\n- two\n'
        assert wikiutil.detect_markup(text) == 'markdown'

    def test_markdown_setext_and_code(self):
        text = 'Title\n=====\n\n```python\nx = 1\n```\n'
        assert wikiutil.detect_markup(text) == 'markdown'

    def test_wiki(self):
        text = "= Title =\n\n'''bold''' text\n\n * one\n * two\n\n||a||b||\n"
        assert wikiutil.detect_markup(text) == 'wiki'

    def test_wiki_with_comments(self):
        text = ('##master-page:FooTemplate\n#language en\n'
                '## these are just samples\n<<Include(Foo)>>\n## and more comments\n')
        assert wikiutil.detect_markup(text) != 'markdown'

    def test_plain_text_is_not_decided(self):
        assert wikiutil.detect_markup('Just some text.\n\nAnother paragraph.\n') is None
        assert wikiutil.detect_markup('') is None

    def test_format_line_wins(self):
        assert wikiutil.detect_markup('#format wiki\n# Title\n**x**\n') is None

    def test_markup_inside_code_is_ignored(self):
        text = "{{{\n# not a heading\n**not bold**\n[x](y)\n}}}\n= Title =\n"
        assert wikiutil.detect_markup(text) == 'wiki'

    def test_page_uses_detected_markup(self):
        page = Page(self.request, PAGENAME)
        page.set_raw_body('# Title\n\nSome **bold** and [a link](FrontPage).\n')
        assert page.pi['format'] == 'markdown'
        assert page.data.startswith('# Title')
        page = Page(self.request, PAGENAME)
        page.set_raw_body("= Title =\n'''bold'''\n")
        assert page.pi['format'] == 'wiki'

    def test_autodetect_off(self):
        self.request.cfg.markup_autodetect = False
        try:
            page = Page(self.request, PAGENAME)
            page.set_raw_body('# Title\n\nSome **bold** and [a link](FrontPage).\n')
            assert page.pi['format'] == self.request.cfg.default_markup
        finally:
            self.request.cfg.markup_autodetect = True


coverage_modules = ['MoinMoin.parser.text_markdown']
