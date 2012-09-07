#!/usr/bin/env python

import os

from gi.repository import GObject, Gio
from gi.repository import TelepathyGLib as Tp

def approve_channel_cb (approver, account, connection,
    channels, dispatch, context, data):
    print "Asked for approval"
    handler = None

    context.accept ()

    for h in dispatch.get_property ("possible-handlers"):
        if h.startswith('org.freedesktop.Telepathy.Client.Phoenix'):
            handler = h

    if handler == None:
        print "No Phoenix handler, closing"
        dispatch.close_channels_async (None, None)
    else:
        print "Handling with: " + handler
        dispatch.handle_with_async (handler, None, None)

if __name__ == '__main__':
    Tp.debug_set_flags(os.getenv('PHOENIX_DEBUG', ''))

    loop = GObject.MainLoop()

    am = Tp.AccountManager.dup()
    approver = Tp.SimpleApprover.new_with_am(am,
        'Phoenix.Approver', False, approve_channel_cb, None)

    approver.add_approver_filter({})
    approver.register()

    loop.run()
