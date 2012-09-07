#!/usr/bin/env python

import os
import sys
import getopt
import tempfile
import shutil
import time
import signal
from util import spawnbus, setup_data_dir
from util import setup_run_dir, create_account, scrub_env

from gi.repository import GObject, Gio, GLib
from gi.repository import TelepathyGLib as Tp

class TestCase:
    def __init__ (self, loop, test_contact, quiet = False):
        self.loop = loop
        self.quiet = quiet
        self.test_contact = test_contact

    def assertNotEqual (self, expected, value):
        if expected == value:
            self.done(False)
            raise AssertionError("didn't expect: %s, got: %s",
                str(expected), str(value))

    def assertEqual (self, expected, value):
        if expected != value:
            self.done(False)
            raise AssertionError("expected: %s, got: %s",
                str(expected), str(value))

    def assertNotNone (self, value):
        if value == None:
            self.done(False)
            raise AssertionError("value was None")

    def done (self, success = True):
        self.loop.quit()
        if not success:
            print "VOIP Test: FAILED"
        else:
            print "VOIP Test: PASS"

    def bite (self):
        # Bitten by the watchdog
        print "Timeout hit"
        self.done (False)

    def set_timeout (self, timeout = 10):
        GLib.timeout_add_seconds (timeout, self.bite)

    def write (self, string):
        if not self.quiet:
            print string

    def set_account (self, cm, protocol, *settings):
        self.cm = cm
        self.protocol = protocol
        self.settings = {}
        self.password = None

        for s in settings:
            (k, v) = s.split("=", 2)
            (t, v) = v.split(":", 2)

            if k == "password":
                self.password = v
                continue

            if t == "b":
                variant = GLib.Variant (t,
                    v in [ "1", "True", "true", "t"])
            else:
                variant = GLib.Variant (t, v)

            self.settings[k] = variant

# Watch one Telepathy connection
class TestConnection:
    def __init__ (self, t, connection):
        self.t = t
        self.connection = connection
        self.contact = None
        self.fully_subscribed = False
        self.call_success = False

        self.connection.connect ('notify::contact-list-state',
                        self.contact_list_state_cb, None)

        if connection.get_contact_list_state() == Tp.ContactListState.SUCCESS:
            self.start_test()

    def contact_list_state_cb (self, connection, spec, data):
        if connection.get_contact_list_state() == Tp.ContactListState.SUCCESS:
            self.start_test()

    def teardown_cb (self, contact, result, u):
        contact.remove_finish (result)

    def teardown(self):
        self.contact.remove_async (self.teardown_cb, None)

    def start_test(self):
        self.connection.dup_contact_by_id_async (
            self.t.test_contact,
            [ Tp.ContactFeature.SUBSCRIPTION_STATES,
              Tp.ContactFeature.CAPABILITIES],
            self.got_test_contact, None)

    def hangup (self):
        self.channel.hangup_async (Tp.CallStateChangeReason.USER_REQUESTED,
            "", "", None, None)

    def check_call_status (self, *args):
        (state, flags, details, reason) = self.channel.get_state()
        got_audio = self.proxy.get_cached_property ("ReceivingAudio")
        got_video = self.proxy.get_cached_property ("ReceivingVideo")

        if state == Tp.CallState.ACTIVE and got_audio and got_video:
            self.t.write("Successful call, letting it run for 5 seconds")
            self.call_success = True
            GLib.timeout_add_seconds (5, self.hangup)

        if state == Tp.CallState.ENDED:
            self.t.assertEqual(True, self.call_success)
            self.t.assertEqual(Tp.CallStateChangeReason.USER_REQUESTED,
              reason.reason)
            self.t.assertEqual (self.connection.get_self_handle (),
                reason.actor)
            self.t.done()

    def create_channel_finished (self, req, r, u):
        try:
            self.channel = channel = req.create_and_observe_channel_finish (r)
        except Exception, e:
            print e
            print e.message
            self.t.done(False)

        d = Gio.bus_get_sync (Gio.BusType.SESSION, None)
        self.proxy = proxy = Gio.DBusProxy.new_sync (d, 0, None,
            "org.freedesktop.Telepathy.Phoenix.Calls",
            "/org/freedesktop/Telepathy/Phoenix/Calls" +
                channel.get_object_path(),
            "org.freedesktop.Telepathy.Phoenix.CallInfo",
            None)
        proxy.connect ("g-properties-changed",
            self.check_call_status, None)
        channel.connect ("notify::state",
            self.check_call_status, None)

    def handle_capabilities (self):
        if self.contact.get_capabilities().supports_audio_video_call (
            Tp.HandleType.CONTACT):
          a = self.contact.get_account()
          req = Tp.AccountChannelRequest.new_audio_video_call (a, 0)
          req.set_target_contact (self.contact)
          req.set_hint ("call-mode", GLib.Variant('s', "test-inputs"))
          req.create_and_observe_channel_async ( "", None,
                    self.create_channel_finished, None)

    def handle_test_contact_states (self):
        p = self.contact.get_publish_state ()
        s = self.contact.get_subscribe_state ()

        if p == Tp.SubscriptionState.YES and s == Tp.SubscriptionState.YES:
            if not self.fully_subscribed:
                self.fully_subscribed = True
                self.t.write ("Subscription complete")
        elif p == Tp.SubscriptionState.ASK:
            self.contact.authorize_publication_async (
                lambda c, r, u: c.authorize_publication_finish (r), None)

    def contact_states_cb (self, c, spec, d):
        self.handle_test_contact_states ()

    def got_test_contact (self, c, r, u):
        self.contact = c.dup_contact_by_id_finish (r)
        s = self.contact.get_subscribe_state ()
        # If we're not subscribed, subscribe, needed to make calls for example
        if s != Tp.SubscriptionState.YES:
            print "Asking for subscription"
            self.contact.request_subscription_async ("Test subscription",
                lambda c, r, u: c.request_subscription_finish (r) ,
                None)

        self.contact.connect ("notify::publish-state", self.contact_states_cb,
            None)
        self.contact.connect ("notify::subscribe-state", self.contact_states_cb,
            None)
        self.contact.connect ("notify::capabilities",
            lambda *x: self.handle_capabilities(), None)
        self.handle_capabilities ()
        self.handle_test_contact_states ()

class TestAccount:
  def __init__ (self, t, account):
    self.t = t
    self.account = account

    self.t.assertEqual (False, account.is_enabled())

    self.account.connect("notify::connection-status",
        self.connection_status_cb, None)
    self.account.connect("notify::connection",
        self.connection_cb, None)

    # Enable & Request availability, causing our connection to be setup
    self.account.set_enabled_async (True, None, None)
    self.account.request_presence_async (
        Tp.ConnectionPresenceType.AVAILABLE,
        "",
        "",
        None, None)

  def connection_test_if_possible (self):
    s = self.account.get_property ("connection-status")
    self.t.assertNotEqual (Tp.ConnectionStatus.DISCONNECTED, s)

    c = self.account.get_property ("connection")
    if s == Tp.ConnectionStatus.CONNECTED and c != None:
        TestConnection (self.t, c)

  def connection_status_cb (self, account, spec, data):
    self.connection_test_if_possible ()

  def connection_cb (self, account, spec, data):
    self.connection_test_if_possible ()

# Watch the account manager
class TestManager:
  def __init__ (self, t):
    self.t = t
    self.am = am = Tp.AccountManager.dup()
    factory = am.get_factory()
    factory.add_account_features ([Tp.Account.get_feature_quark_connection ()])
    factory.add_connection_features ([
       Tp.Connection.get_feature_quark_contact_list ()])
    self.accounts = {}

    am.prepare_async(None, self.prepared, None)

  def got_account (self, account):
    self.t.assertNotNone(account)
    TestAccount (self.t, account)

  def prepared (self, am, result, data):
    # We start in a temporary session without existing accounts
    self.t.assertEqual([], am.get_valid_accounts())
    # Create fresh acocunt
    create_account (self.am,
        self.t.cm, self.t.protocol,
        "Phoenix Test Account",
        self.t.settings,
        self.t.password,
        self.got_account)

if __name__ == '__main__':
    quiet = False
    datadir = None
    testcontact = None
    try:
        opts, args = getopt.getopt(sys.argv[1:],
            "q", ["datadir=", "quiet", "testcontact="])
        for o, a in opts:
            if o == "--datadir":
                datadir = a
            elif o in [ "-q", "--quiet"]:
                quiet = True
            elif o == "--testcontact":
                testcontact = a
        if testcontact == None:
            print "Testcontact option is required"
            sys.exit(2)
        if len(args) < 3:
            print "Execpect account argument: CM protocol settings"
            sys.exit(2)
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)

    # Use a temporary directory for the testrun
    tempdir = tempfile.mkdtemp(prefix="phoenix-test")
    setup_run_dir(tempdir, quiet=quiet)
    if datadir != None:
        setup_data_dir(datadir, quiet)

    scrub_env()
    p = spawnbus(quiet)
    loop = GObject.MainLoop()
    t = TestCase (loop, testcontact, quiet)
    t.set_timeout (30)
    t.set_account (*args)

    Tp.debug_set_flags(os.getenv('PHOENIX_TEST_DEBUG', ''))

    m = TestManager(t)
    try:
        loop.run()
    finally:
        os.kill (p.pid, signal.SIGKILL)
        # Sleep 2 seconds so everything can die a nice death
        time.sleep (2)
        shutil.rmtree(tempdir)
