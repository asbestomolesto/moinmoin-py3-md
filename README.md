<!-- Written by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026 (moinmoin-py3-md 1.12.0). -->
# moinmoin-py3-md

**MoinMoin 1.9 for Python 3, with Markdown pages.**

moinmoin-py3-md (MoinMoin 1.12.0) is the classic
[MoinMoin](https://moinmo.in/) 1.9 wiki engine, ported to Python 3 and
packaged for current GNU/Linux distributions. It can also hold pages written
in **Markdown**, next to the pages written in MoinMoin wiki syntax.

- Based on MoinMoin 1.9.11, the last release of the 1.9 series, which runs
  only on Python 2.
- Runs on Python 3.9 or newer (tested with 3.11, 3.12 and 3.13).
- Existing 1.9 wikis work without converting their data.
- Markdown and MoinMoin wiki pages can be mixed in one wiki. The markup of
  each page is recognized from its text.
- Packages: `.deb` (Devuan, Debian, Ubuntu), `.rpm` (Fedora), Python wheel.
- Does not need systemd. A sysvinit init script is included, and the wiki
  also runs inside Apache, nginx with uWSGI, gunicorn, or as CGI, FastCGI or
  SCGI.

This project is not MoinMoin 2.0 ([moinwiki/moin](https://github.com/moinwiki/moin)),
which is a rewrite with a different data format. moinmoin-py3-md keeps the
1.9 code, data format, themes and plugin interface.

## Installation

Download the packages from the
[Releases](https://github.com/asbestomolesto/moinmoin-py3-md/releases) page.

**Devuan, Debian, Ubuntu and derivatives** (one package for all of them):

    sudo apt install ./moinmoin-py3-md_1.12.0-1_all.deb

**Fedora and other RPM distributions:**

    sudo dnf install ./moinmoin-py3-md-1.12.0-1.fc42.noarch.rpm

**Any distribution, with pip:**

    python3 -m venv /opt/moin
    /opt/moin/bin/pip install moinmoin_py3_md-1.12.0-py3-none-any.whl

With pip, the wiki templates (`data`, `underlay`, `config/wikiconfig.py`)
are installed under `/opt/moin/share/moin/`. To make a wiki, copy them into a
directory and edit `wikiconfig.py`. The `moin-mkwiki` helper comes only with
the .deb and .rpm packages.

The packages replace `python3-moinmoin` (1.10.0), `python3-moinmoin-markdown`
and `moin-markdown` (1.11.0+mdN), the earlier releases of this work.

## Quick start (.deb)

    sudo moin-mkwiki -n "My Wiki" -s AdminUser /srv/moin/mywiki
    sudo -u www-data moin --config-dir=/srv/moin/mywiki --wiki-url=http://localhost/ \
         account create --name=AdminUser --email=admin@example.org --password='...'
    # standalone server: set INSTANCES="mywiki:/srv/moin/mywiki:8080" in /etc/default/moinmoin
    sudo service moinmoin start

Open http://localhost:8080/, log in as AdminUser, open the page
**LanguageSetup** and install the help and system pages
(e.g. `English--all_pages.zip`). The pages appear after the wiki is
restarted, as in the original MoinMoin.

The full guide is [docs/GUIDE.md](docs/GUIDE.md). It covers web servers,
migrating a 1.9 wiki, security settings and building the packages.

## Markdown pages

Write the page in Markdown and MoinMoin recognizes it. It looks for
constructs typical of each markup:

- Markdown: `# Title`, `**bold**`, `[text](link)`, lists at the start of a
  line, ```` ``` ```` blocks;
- MoinMoin wiki: `= Title =`, `'''bold'''`, `||tables||`, `{{{code}}}`,
  indented lists.

Text that is clearly neither of the two, such as plain text, uses the
default markup (MoinMoin wiki). A first line always overrides the
recognition:

    #format markdown

or `#format moin` for MoinMoin wiki syntax. The old `#format wiki` still
works. New pages can also be created from the **MarkdownTemplate** page.
Existing pages are never modified or converted.

| What | Syntax |
|---|---|
| link to a page | `[[PageName]]`, `[[PageName\|text]]`, `[text](PageName)` |
| relative pages | `[text](/SubPage)`, `[text](../SiblingPage)` |
| interwiki | `[[MoinMoin:HelpOnMacros]]` |
| attachments | `[[attachment:file.pdf\|text]]`, `![description](attachment:image.png)` |
| external links | `[text](https://...)`, `<https://...>` |
| MoinMoin macros | `<<TableOfContents>>`, `<<FullSearch(...)>>`, ... |
| highlighted code | ```` ```python ```` ... ```` ``` ```` |
| wiki syntax inside Markdown | ```` ```wiki ```` block (also `creole`, `rst`, `csv`) |
| tables, footnotes, definition lists, abbreviations | extended Markdown syntax |

Markdown pages work like wiki pages in search, RecentChanges, backlinks,
LocalSiteMap, history and diffs, attachments, renaming, `<<TableOfContents>>`
and the page cache. The help page **HelpOnMarkdown** describes the syntax.
The help pages of all the language packs link to it.

Raw HTML in a Markdown page is shown as text, never rendered. Links accept
only safe URL schemes (`http`, `https`, `ftp`, `mailto`, ...).

Options in `wikiconfig.py`:

    markup_autodetect = False      # turn off the recognition of the markup
    default_markup = 'markdown'    # markup of the pages that are not recognized
    markdown_extensions = ['tables', 'footnotes', 'def_list', 'abbr', 'sane_lists']  # default

## Changes from MoinMoin 1.9.11

- Python 3 port of the whole code base. The bundled pygments, passlib and
  parsedatetime are replaced by the system packages, flup is updated to
  1.0.3, and Werkzeug 1.0.1 stays bundled.
- Markdown pages and automatic recognition of the page markup.
- Security fixes:
  - limits on the form data of a request: one anonymous request could
    exhaust the memory or the CPU of the server (CVE-2023-25577 in the
    bundled Werkzeug);
  - linear time for markup recognition and the Markdown parser on hostile
    pages;
  - `HttpOnly` session cookie by default;
  - escaping in the OpenID teams extension.
- Fixes:
  - RFC 6266 `Content-Disposition` header, so non-ASCII attachment names
    work in every browser;
  - the page cache is tied to the Python version;
  - `<<TableOfContents>>` in the preview of unsaved pages.
- Static files are served under `/moin_static1120`. Update an Apache `Alias`
  or nginx `location` that serves them directly.

The details are in [docs/CHANGES](docs/CHANGES) and in the git history: each
change is a separate commit, starting from the original 1.9.11 release.

### Version history

| Version | What |
|---|---|
| 1.10.0 | MoinMoin 1.9.11 ported to Python 3, Debian package |
| 1.11.0+md1 | Markdown pages |
| 1.11.0+md2 | Automatic recognition of the page markup, `#format moin`, help pages in all languages |
| 1.11.0+md3 | Security fixes, RPM and pip packages |
| **1.12.0** | One project (moinmoin-py3-md): new package names, version accepted by PyPI, English documentation, CI builds |

## Known limitations

- The Jabber/XMPP notification bot does not work. It needs pyxmpp, which
  exists only for Python 2.
- The DocBook and XSLT parsers do not work. They need 4Suite, which exists
  only for Python 2.
- OpenID, LDAP, xapian and MySQL: the code is ported but has not been tested
  against those services.
- The graphical editor works only with wiki syntax pages. Markdown pages are
  edited with the text editor.
- Markdown pages do not turn CamelCase words into links. This is
  intentional.

## Building and testing

    python3 -m pytest MoinMoin           # test suite (needs python3-markdown)
    python3 -m build                     # wheel and sdist
    dpkg-buildpackage -us -uc -b         # .deb (see docs/GUIDE.md)
    rpmbuild -ta moinmoin-py3-md-1.12.0.tar.gz   # .rpm

The GitHub Actions workflow in `.github/workflows/build.yml` runs the tests
on every push. On a version tag it builds all the packages, installs them on
several distributions and attaches them to the GitHub release.

## Authors and license

- **MoinMoin**: Juergen Hermann, Thomas Waldmann and the MoinMoin developers.
- **Python 3 port, Markdown support, security fixes and packages**:
  Gabriele 'asbesto' Zaverio <asbesto@freaknet.org>, with the assistance of
  Claude (Anthropic AI).

A comment at the top of each file written or modified by Claude says so. In
the git history every commit after the first, which contains the original
MoinMoin 1.9.11, has the line `Co-Authored-By: Claude`.

License: GNU GPL version 2 or later, see [COPYING](COPYING). The bundled
third party code keeps its own license, see `docs/licenses/` and
`debian/copyright`.
