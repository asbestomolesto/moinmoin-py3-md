<!-- Written by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026 (moinmoin-py3-md 1.12.0). -->
# moinmoin-py3-md guide

This guide covers installing, running and maintaining moinmoin-py3-md
(MoinMoin 1.12.0). For an overview see the [README](../README.md). The
installed Debian package also has `/usr/share/doc/moinmoin-py3-md/README.Debian`
and the manual pages `man moin` and `man moin-mkwiki`.

## Packages

| File | For |
|---|---|
| `moinmoin-py3-md_1.12.0-1_all.deb` | Devuan, Debian, Ubuntu and derivatives |
| `moinmoin-py3-md_1.12.0-1.dsc`, `*.orig.tar.gz`, `*.debian.tar.xz` | Debian source package |
| `moinmoin-py3-md-1.12.0-1.fc42.noarch.rpm`, `*.src.rpm` | Fedora and other RPM distributions |
| `moinmoin_py3_md-1.12.0-py3-none-any.whl`, `moinmoin_py3_md-1.12.0.tar.gz` | pip, any distribution |
| `moinmoin-py3-md-1.12.0.tar.gz` | source tree (also used by `rpmbuild -ta`) |
| `SHA256SUMS` | checksums |

Check the downloads with `sha256sum -c SHA256SUMS`.

apt and dnf install the dependencies themselves: Python-Markdown,
Pygments, passlib, parsedatetime and, on Python 3.13 or newer, legacy-cgi.
Other RPM distributions can rebuild the source package with
`rpmbuild --rebuild moinmoin-py3-md-1.12.0-1.fc42.src.rpm`.

The packages replace `python3-moinmoin` (1.10.0), `python3-moinmoin-markdown`
and `moin-markdown` (1.11.0+mdN). They provide the same `MoinMoin` module
and `moin` command, so only one of them can be installed. Wikis work with
all of them, but the older 1.10.0 shows Markdown pages as plain text.

## Creating a wiki

With the .deb or .rpm package:

    sudo moin-mkwiki -n "My Wiki" -l en -s AdminUser /srv/moin/mywiki
    sudo -u www-data moin --config-dir=/srv/moin/mywiki --wiki-url=http://localhost/ \
         account create --name=AdminUser --email=admin@example.org --password='...'

On Fedora the wiki files belong to the user `apache` instead of `www-data`.
`moin-mkwiki -u USER -g GROUP` chooses another owner.

`moin-mkwiki -s NAME` makes NAME the superuser and gives it all the ACL
rights (`acl_rights_before`), as the sample configuration suggests. Without
it, with the default ACLs, a logged-in user can only read. The new wiki
gets a random `secrets` value.

Then log in as AdminUser, open the page **LanguageSetup** and install the
page package of your language (e.g. `English--all_pages.zip`). The pages
appear after the wiki is restarted, as in the original MoinMoin.

With pip, copy the templates from `<venv>/share/moin/` (`data`, `underlay`,
`config/wikiconfig.py`, `server/`) into a new directory, edit
`wikiconfig.py` and set a long random value for `secrets` there.

## Running the wiki

All the example files are in `/usr/share/doc/moinmoin-py3-md/examples/`
(with the .deb and the .rpm packages).

- **Standalone server with sysvinit (Devuan):** in `/etc/default/moinmoin`
  set for example `INSTANCES="mywiki:/srv/moin/mywiki:8080"`, then run
  `sudo service moinmoin start`. The init script is enabled at boot and does
  nothing while `INSTANCES` is empty. Use it on its own for a local wiki, or
  behind nginx or Apache as a reverse proxy (`nginx-proxy.conf`).
- **Apache + mod_wsgi:** `apt install libapache2-mod-wsgi-py3`, example
  `apache-mod_wsgi.conf`.
- **nginx + uWSGI:** `apt install uwsgi uwsgi-plugin-python3 nginx`,
  examples `uwsgi-mywiki.ini` and `nginx-uwsgi.conf`.
- **gunicorn:**

      cp /srv/moin/mywiki/moin.wsgi /srv/moin/mywiki/moin_wsgi.py
      gunicorn -b 127.0.0.1:8080 --chdir /srv/moin/mywiki moin_wsgi:application

  and `nginx-proxy.conf` in front of it.
- **CGI, FastCGI (Apache mod_fcgid, lighttpd), SCGI:** the scripts
  `moin.cgi`, `moin.fcgi`, `moin.scgi` of the instance, examples
  `apache-cgi.conf`, `apache-fcgid.conf`, `lighttpd-fastcgi.conf`.
- **systemd systems:** `moinmoin.service`. The init script also works
  through the SysV generator.

The data directory must be writable by the user running the wiki.

The static files (CSS, JavaScript, images) are served under
**`/moin_static1120`**. The prefix depends on the version: it was
`/moin_static1911` with 1.9.11, `/moin_static1100` with 1.10.0 and
`/moin_static1110` with 1.11.0+mdN. If the web server serves them directly
with an `Alias`, update it as in the examples.

## Migrating an existing 1.9 wiki

The data format did not change. Pages, users, edit logs and attachments
written by MoinMoin on Python 2 are read by this version, and the other
way round. This was checked in both directions.

1. Create an instance with `moin-mkwiki`.
2. Replace its `data/` with the one of the old wiki, and also `underlay/` if
   it was modified. Give them to the wiki user (`chown -R www-data: ...`).
3. Copy the settings of the old `wikiconfig.py` into the new one. The
   syntax must be Python 3: for example, no `print x` statements.
4. Optionally run
   `moin --config-dir=... --wiki-url=... maint cleancache`. Old caches
   are ignored and recreated anyway.
5. Third party plugins in `data/plugin/` must be ported to Python 3.

## Markdown pages

The [README](../README.md#markdown-pages) has the syntax summary. Some more
details:

- Markup recognition was tested on all the system and help pages of
  MoinMoin with their `#format` line removed: none was taken for Markdown.
  Of 903 Markdown files found on a system it recognized 848. The others are
  almost all plain text, which also looks right as wiki syntax.
- Recognition looks only at the first 64 KiB of a page.
- In a Markdown page, `# Title` and `## Section` lines at the top are
  headings, not MoinMoin processing instructions or comments. Only the
  comments MoinMoin writes itself stay comments, such as
  `## page was renamed from ...`.
- The Python-Markdown extensions are chosen with `markdown_extensions` in
  `wikiconfig.py`. The default is
  `['tables', 'footnotes', 'def_list', 'abbr', 'sane_lists']`.

## Security

Limits on the data sent to the wiki, in `wikiconfig.py`, with their
defaults:

    max_form_memory_size = 16 * 1024 * 1024  # form fields kept in memory
    max_form_parts = 1000                    # parts of a multipart request
    max_content_length = None                # whole request (attachments)

Bigger requests get "413 Request Entity Too Large". Before these limits,
one form submission by an anonymous user could exhaust the memory of the
server (CVE-2023-25577 in the bundled Werkzeug). Uploaded files do not
count against the memory limit. A limit for the whole request can also be
set in the web server (Apache `LimitRequestBody`, nginx
`client_max_body_size`).

Other protections:

- Markup recognition and the Markdown parser run in linear time, even on
  pages made with thousands of unclosed brackets, code spans, links or
  headings.
- The session cookie is `HttpOnly` by default (`cookie_httponly = True`),
  so scripts in the browser cannot read it.
- By default only "Trusted" users may edit pages (`acl_rights_default`).

Recommendations:

- The standalone server (`moin ... server standalone`, `/etc/init.d/moinmoin`)
  is the Werkzeug development server and listens on 127.0.0.1. Do not
  expose it to the Internet directly: put a web server in front of it
  (`nginx-proxy.conf`), or use Apache mod_wsgi or uWSGI.
- Never enable `debug='web'` on a public wiki.
- With a pip installation, set a long random value for `secrets` in
  `wikiconfig.py`. `moin-mkwiki` does this itself.
- XML-RPC is off by default, as in the original MoinMoin. To enable it,
  remove `xmlrpc` from `actions_excluded` in `wikiconfig.py`.

## What was tested

- Test suite: 521 passed, 132 skipped (optional modules such as xapian and
  ldap are missing), 1 expected failure that already fails in the original
  1.9.11.
- Comparison with the original MoinMoin 1.9.11 on Python 2.7.18:
  - all 1,895 help pages rendered to HTML. The remaining differences come
    from the Pygments and mimetypes versions, string `repr` and random
    content;
  - an HTTP scenario of 65 requests (accounts, login, edit and save,
    attachments, copy, rename, delete, search, RSS, XML-RPC): 58 identical
    responses, harmless differences in the rest;
  - the `moin` commands (account, export, import, maint, ...).
- Ways to run it: standalone server (also through `/etc/init.d/moinmoin`),
  WSGI (the standard library validator, gunicorn), CGI, FastCGI, SCGI.
- Apache 2.4 + mod_wsgi in daemon mode, configured from the package
  example:
  - login and installation of a language pack;
  - pages with accented names and text;
  - diff and info;
  - a 100 KB binary attachment uploaded and downloaded unchanged;
  - rename with attachments, search, RSS;
  - XML-RPC v1 and v2, including writes with an authentication token;
  - static files served by Apache;
  - 270 reads and 30 writes in parallel without server errors. Of 10
    simultaneous writes of the same page, one is refused with "page is
    being edited". This is MoinMoin's original locking, and the data stays
    consistent.
- Security review: 82 attempts to inject scripts into Markdown pages had
  no effect, hostile inputs up to 160 KB ran in linear time, the form
  limits were checked over HTTP (413), and login, saving and a 30 MB
  attachment worked.
- Packages: an automatic test installs the package, creates a wiki,
  installs a language pack and starts the server. It then checks login,
  Markdown and wiki pages recognized from their text, `#format moin` and
  the links to the help pages.
  - 1.11.0+md3 passed it on Devuan 6, 5 and 4, Debian 13, 12 and 11,
    Ubuntu 24.04 and 22.04 (.deb), Fedora 42 and 41 (.rpm), and Python
    3.13, 3.12 and 3.11 (wheel).
  - 1.12.0 has the same code; its packages are installed and checked by
    the GitHub Actions workflow.
- lintian reports no errors on the .deb.

## Building from source

Debian, Devuan, Ubuntu:

    sudo apt install debhelper dh-python pybuild-plugin-pyproject python3-all python3-setuptools
    dpkg-source -x moinmoin-py3-md_1.12.0-1.dsc
    cd moinmoin-py3-md-1.12.0 && dpkg-buildpackage -us -uc

or `dpkg-buildpackage -us -uc -b` directly in a git checkout.

Fedora:

    sudo dnf install rpm-build python3-devel pyproject-rpm-macros
    rpmbuild -ta moinmoin-py3-md-1.12.0.tar.gz

Python wheel and sdist: `python3 -m build`.

Tests, from the source tree: `python3 -m pytest MoinMoin` (needs
Python-Markdown, Pygments, passlib, parsedatetime and pytest).

## Credits

MoinMoin was written by Juergen Hermann, Thomas Waldmann and the MoinMoin
developers. The Python 3 port, the Markdown support, the security fixes and
the packages were made by Gabriele 'asbesto' Zaverio
<asbesto@freaknet.org>, with the assistance of Claude (Anthropic AI). A
comment at the top of each file written or modified by Claude says so, and
every commit after the first has the line `Co-Authored-By: Claude`.

The maintainer does not have particular skills in Python and made this
project with Claude, so issues and security problems may be beyond what
the maintainer can understand or fix alone; the maintainer will do their
best, using AI to help. Anyone more skilled is welcome to fork this project and maintain it.
See "About the maintainer" in the [README](../README.md#about-the-maintainer).
