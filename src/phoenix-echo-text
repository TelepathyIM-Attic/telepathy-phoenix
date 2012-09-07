#!/usr/bin/env python

import os

from gi.repository import GObject, Gio
from gi.repository import TelepathyGLib as Tp

class TextEchoer:
    def __init__ (self, channel):
        self.channel = channel
        self.channel.connect ('message-received', self.got_message, None)
        self.ack_pending ()

    def send_text (self, text):
        print "Sending %s" % text
        m = Tp.ClientMessage.new_text (Tp.ChannelTextMessageType.NORMAL,
            text)
        self.channel.send_message_async (m, 0, None, None)

    def got_message (self, channel, msg, data):
        text, flags = msg.to_text()
        self.send_text (text)
        channel.ack_message_async (msg, None, None)

    def ack_pending (self):
        messages = self.channel.get_pending_messages ()
        for m in messages:
            text, flags = m.to_text()
            self.send_text (text)

        self.channel.ack_messages_async (messages, None, None)

def handle_channels_cb (handler, account, connection,
    channels, satisfied, action_time, context, data):
    print "Asked to handle"

    for c in channels:
        TextEchoer (c)

    context.accept ()

if __name__ == '__main__':
    Tp.debug_set_flags(os.getenv('PHOENIX_DEBUG', ''))

    loop = GObject.MainLoop()

    am = Tp.AccountManager.dup()
    factory = am.get_factory()

    factory.add_channel_features (
        [Tp.TextChannel.get_feature_quark_incoming_messages ()])

    handler = Tp.SimpleHandler.new_with_am(am, False, False,
        'Phoenix.EchoText', False, handle_channels_cb, None)

    handler.add_handler_filter({
        Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,
        Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT)})
    handler.register()

    loop.run()
