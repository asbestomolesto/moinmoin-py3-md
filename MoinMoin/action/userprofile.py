# -*- coding: iso-8859-1 -*-
# Modified by Claude (Anthropic AI) (moinmoin-py3-md 1.12.1): disabled accounts
# are found (the "Enable user" button created an empty account instead), the
# disabled flag uses User.disable/enable, new "Delete user" button.
"""
    MoinMoin - set values in user profile

    @copyright: 2008 MoinMoin:ThomasWaldmann
    @license: GNU GPL, see COPYING for details.
"""
from MoinMoin.Page import Page
from MoinMoin import user, wikiutil

def execute(pagename, request):
    """ set values in user profile """
    _ = request.getText
    cfg = request.cfg
    form = request.form

    if not request.user.isSuperUser():
        request.theme.add_msg(_("Only superuser is allowed to use this action."), "error")
    elif (request.method == 'POST' and
          wikiutil.checkTicket(request, form.get('ticket', ''))):
        user_name = form.get('name', '')
        key = form.get('key', '')
        val = form.get('val', '')
        uid = user.getUserIdIncludingDisabled(request, user_name)
        theuser = user.User(request, uid)
        if not uid or not theuser.exists():
            request.theme.add_msg(_('User account "%s" not found.') % wikiutil.escape(user_name), "error")
        elif key == 'delete':
            theuser.delete()
            request.theme.add_msg(_('User account "%s" deleted.') % wikiutil.escape(user_name), "info")
        elif key == 'disabled':
            changed = theuser.disable() if val == '1' else theuser.enable()
            if changed:
                if theuser.disabled:
                    msg = _('User account "%s" disabled.')
                else:
                    msg = _('User account "%s" enabled.')
                request.theme.add_msg(msg % wikiutil.escape(theuser.name), "info")
        else:
            if key in [k for k, label in cfg.user_checkbox_fields]:
                val = int(val)
            oldval = getattr(theuser, key)
            setattr(theuser, key, val)
            theuser.save()
            request.theme.add_msg('%s.%s: %s -> %s' % tuple([wikiutil.escape(str(s)) for s in [user_name, key, oldval, val]]), "info")

    Page(request, pagename).send_page()

