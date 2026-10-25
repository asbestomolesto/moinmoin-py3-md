<!-- Written by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026 (moinmoin-py3-md 1.12.0). -->
# Security policy

## Supported versions

| Version | Supported |
|---|---|
| 1.12.x | yes |
| 1.11.0+mdN, 1.10.0 | no, please update to 1.12 |

This project covers moinmoin-py3-md only, the Python 3 version of
MoinMoin 1.9. Problems in the original Python 2 MoinMoin 1.9 belong to
[moinwiki/moin-1.9](https://github.com/moinwiki/moin-1.9), and problems in
MoinMoin 2.0 belong to [moinwiki/moin](https://github.com/moinwiki/moin).

## Reporting a vulnerability

Please do **not** open a public issue for a security problem. Report it
privately, in one of these ways:

- the **Report a vulnerability** button in the
  [Security tab](https://github.com/asbestomolesto/moinmoin-py3-md/security)
  of this repository;
- email to Gabriele 'asbesto' Zaverio <asbesto@freaknet.org>.

Please include:

- the affected version;
- how the wiki is run (standalone server, Apache mod_wsgi, uWSGI, ...);
- the steps or the page text that show the problem;
- what an attacker gains: without login, with an account, or with write
  access to pages.

You will get an answer within two weeks. When the fix is released, the
report is credited in `docs/CHANGES`, unless you prefer otherwise.

## Security settings

The settings that limit the requests (`max_form_memory_size`,
`max_form_parts`, `max_content_length`), and the recommendations for
running a public wiki, are in the "Security" section of
[docs/GUIDE.md](docs/GUIDE.md#security).
