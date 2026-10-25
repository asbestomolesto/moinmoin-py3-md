#!/bin/sh
# Written by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026 (moinmoin-py3-md 1.12.0).
# Smoke test of an installed moinmoin-py3-md package: creates a wiki with
# moin-mkwiki, starts the standalone server and checks a Markdown page and
# a MoinMoin wiki page, both without a #format line.
#
# Usage: smoke-test.sh [WIKI_USER]   (run as root; WIKI_USER default www-data)

set -e

WUSER=${1:-www-data}
TOP=$(mktemp -d)
chmod 755 "$TOP"
WIKI=$TOP/wiki
PORT=8080
BASE=http://127.0.0.1:$PORT

id "$WUSER" >/dev/null 2>&1 || useradd -r -M -s /sbin/nologin "$WUSER"
moin-mkwiki -n "Smoke Test" -s AdminUser -u "$WUSER" -g "$WUSER" "$WIKI" >/dev/null

# a page is a directory with a "current" file naming the latest revision
mkpage() {
    mkdir -p "$WIKI/data/pages/$1/revisions"
    printf '00000001\n' > "$WIKI/data/pages/$1/current"
    printf '%s\n' "$2" > "$WIKI/data/pages/$1/revisions/00000001"
    chown -R "$WUSER:" "$WIKI/data/pages/$1"
}
mkpage MarkdownSmoke "$(printf '# Markdown heading\n\nSome **bold** text and [a link](https://example.org/md).\n\n- one\n- two\n')"
mkpage WikiSmoke "$(printf "= Wiki heading =\n\nSome '''bold''' text and [[https://example.org/wiki|a link]].\n\n || a || b ||\n")"

su -s /bin/sh "$WUSER" -c "cd '$WIKI' && exec moin --config-dir='$WIKI' server standalone --port=$PORT --interface=127.0.0.1" \
    > "$TOP/server.log" 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null || true' EXIT

i=0
until curl -fs -o /dev/null "$BASE/HelpOnMarkdown"; do
    i=$((i + 1))
    if [ $i -gt 30 ]; then cat "$TOP/server.log"; exit 1; fi
    sleep 1
done

fail() { echo "FAIL: $*"; cat "$TOP/server.log"; exit 1; }

help=$(curl -fsS "$BASE/HelpOnMarkdown")
echo "$help" | grep -q "moin_static1120" || fail "static prefix /moin_static1120 not found"
md=$(curl -fsS "$BASE/MarkdownSmoke")
echo "$md" | grep -q 'href="https://example.org/md"' || fail "Markdown link not rendered"
echo "$md" | grep -q '<strong>bold</strong>' || fail "Markdown bold not rendered"
wk=$(curl -fsS "$BASE/WikiSmoke")
echo "$wk" | grep -q 'href="https://example.org/wiki"' || fail "wiki link not rendered"
echo "$wk" | grep -q '<strong>bold</strong>' || fail "wiki bold not rendered"

echo "smoke test passed"
