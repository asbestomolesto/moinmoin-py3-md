# RPM spec of MoinMoin 1.11.0+md3 (Fedora, RHEL/AlmaLinux/Rocky with EPEL
# and other distributions with the pyproject RPM macros).
# Rewritten by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026,
# for MoinMoin 1.11.0+md2; the original spec was by Florian Festi,
# Johannes Poehlmann and Thomas Waldmann (see the changelog below).
#
# Build:  rpmbuild -ta moin-markdown-1.11.0+md3.tar.gz
#    or:  rpmbuild -ba moin.spec  (with the tarball in ~/rpmbuild/SOURCES)

Name:           moin-markdown
Version:        1.11.0+md3
Release:        1%{?dist}
Summary:        MoinMoin wiki with MoinMoin syntax and Markdown pages (Python 3)

License:        GPL-2.0-or-later
URL:            https://moinmo.in/
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)
BuildRequires:  python3dist(pip)

# the runtime dependencies (markdown, pygments, passlib, parsedatetime,
# legacy-cgi on Python >= 3.13) are generated from the package metadata
Provides:       moin = %{version}-%{release}
Conflicts:      moin < 1.10
Recommends:     python3dist(docutils)

%description
MoinMoin is a wiki engine written in Python. It supports many markups
(its own wiki syntax, Creole, reStructuredText, HTML), page history and
diffs, attachments, access control lists, user accounts, search, themes
and plugins.

This is MoinMoin 1.11.0+md3: MoinMoin 1.10.0 (MoinMoin 1.9.11 ported to
Python 3) with pages written in Markdown, next to the pages in MoinMoin
wiki syntax. The markup of a page is recognized from its text, or set
with "#format markdown" / "#format moin". Existing 1.9 wikis can be used
without converting the data.

Made by Gabriele 'asbesto' Zaverio with the assistance of Claude
(Anthropic AI).

%prep
%autosetup -n %{name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
# the tests are not shipped
find %{buildroot}%{python3_sitelib}/MoinMoin -name '_tests' -type d -prune -exec rm -rf {} +
find %{buildroot}%{python3_sitelib}/MoinMoin -name 'conftest.py' -delete
# helper scripts of the FCKeditor static files are not needed
find %{buildroot} -path '*FCKeditor*' \( -name '*.py' -o -name '*.pl' -o -name '*.php' \
     -o -name '*.cfm' -o -name '*.asp' -o -name '*.aspx' -o -name '*.lasso' -o -name '*.cgi' \) -delete
# moin-mkwiki creates a wiki instance (files owned by the web server user)
install -D -m 0755 debian/moin-mkwiki %{buildroot}%{_sbindir}/moin-mkwiki
sed -i -e 's/www-data/apache/g' \
       -e '/README.Debian/s|.*| * run the wiki, see the examples in %{_docdir}/%{name}/examples:|' \
       -e '/init.d\/moinmoin/d' \
       -e 's|/usr/share/doc/python3-moinmoin-markdown|%{_docdir}/%{name}|g' \
       %{buildroot}%{_sbindir}/moin-mkwiki
install -D -m 0644 debian/moin.1 %{buildroot}%{_mandir}/man1/moin.1
install -D -m 0644 debian/moin-mkwiki.8 %{buildroot}%{_mandir}/man8/moin-mkwiki.8
sed -i 's/www-data/apache/g' %{buildroot}%{_mandir}/man8/moin-mkwiki.8
cd %{buildroot}%{_datadir}/moin/server && chmod 0755 moin moin.ajp moin.cgi moin.fcgi moin.scgi test.wsgi

%files
%license docs/licenses/COPYING
%doc README.rst docs/CHANGES docs/INSTALL.html docs/UPDATE.html
%doc debian/examples
%{python3_sitelib}/MoinMoin/
%{python3_sitelib}/moin_markdown-*.dist-info/
%{_bindir}/moin
%{_sbindir}/moin-mkwiki
%{_datadir}/moin/
%{_mandir}/man1/moin.1*
%{_mandir}/man8/moin-mkwiki.8*

%changelog
* Sat Oct 10 2026 Gabriele 'asbesto' Zaverio <asbesto@freaknet.org> - 1.11.0+md3-1
- MoinMoin 1.11.0+md3: security fixes (limits for the form data, Markdown
  pages that crash the parser or keep it busy, linear time recognition of
  the page markup, httponly session cookie)

* Fri Oct 09 2026 Gabriele 'asbesto' Zaverio <asbesto@freaknet.org> - 1.11.0+md2-1
- MoinMoin 1.11.0+md2: Markdown pages, automatic recognition of the page
  markup, "#format moin", help pages with references to Markdown
- Spec rewritten for Python 3 and the pyproject RPM macros (with the
  assistance of Claude, Anthropic AI)

* Mon Sep 5 2016 Thomas Waldmann
- Raised requirement to Python 2.7

* Sun Jan  5 2014 Thomas Waldmann
- Raised requirement to Python 2.5

* Sun Feb 15 2009 Thomas Waldmann
- Raised requirement to Python 2.4
- Removed references to Python 1.5
- Fixed doc files.

* Thu Jun  8 2006 Johannes Poehlmann
- Fix RPM build errror "Files listet twice"
  Replaced files list and just package all of /usr.

* Fri Mar 05 2004 Florian Festi
- Initial RPM release.
