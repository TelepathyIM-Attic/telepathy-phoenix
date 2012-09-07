#!/usr/bin/env python

import os
import sys
import getopt
from util import spawnbus, setup_data_dir, setup_run_dir

from gi.repository import GObject, Gio
from gi.repository import TelepathyGLib as Tp

# Watch one Telepathy connection
class Connection:
    def __init__ (self, connection):
        self.connection = connection
        self.contacts = []
        self.connection.prepare_async (
            [ Tp.Connection.get_feature_quark_contact_list () ],
            self.prepared_cb, None)

    def check_contact (self, contact):
        # Remove from our contact list if the remote removed us
        # Authorize and subscribe to the remote when asked
        p = contact.get_property ("publish-state")
        if p == Tp.SubscriptionState.REMOVED_REMOTELY:
            self.connection.remove_contacts_async ([ contact ], None, None)
        elif p == Tp.SubscriptionState.ASK:
            self.connection.authorize_publication_async ([ contact ],
                None, None )
            self.connection.request_subscription_async ([ contact ],
                "You subscribe to me, I subscribe to you!",
                None, None )

    def subscription_state_changed (self, contact, subscribe, publish,
            request, data):
        self.check_contact (contact)

    def add_contact (self, contact):
        if contact in self.contacts:
            return

        self.contacts.append (contact)
        self.check_contact (contact)
        contact.connect ('subscription-states-changed',
            self.subscription_state_changed, None)

    def remove_contact (self, contact):
        print "Removed: %s" % (contact.get_identifier ())
        self.contacts.remove (contact)

    def contact_list_changed (self, connection, added, removed, data):
        for contact in added:
            self.add_contact (contact)

        for contact in removed:
            self.remove_contact (contact)

    def prepared_cb (self, connection, result, data):
        # Connect for future updates
        self.connection.connect ('contact-list-changed',
            self.contact_list_changed, None)

        if (connection.get_contact_list_state() !=
                Tp.ContactListState.SUCCESS):
            print "Contactlist not retrieved just yet.."
            return
        contacts = connection.dup_contact_list ()
        for c in contacts:
            self.add_contact (c)

# Watch one Telepathy account
class Account:
  def __init__ (self, account):
    self.connection = None
    self.account = account

    self.account.connect("notify::connection", self.connection_changed, None)
    self.setup_connection ()

    # Reuest availability
    self.account.request_presence_async (
        Tp.ConnectionPresenceType.AVAILABLE,
        "",
        "",
        None, None)

  def setup_connection (self):
    c = self.account.get_property("connection")
    if c != None:
        self.connection = Connection (c)
    else:
        self.connection = None

    print "Setup connection for " \
        + self.account.get_property ("display-name") \
        + ": " + str (self.connection)

  def connection_changed (self, account, spec, data):
    self.setup_connection ()

# Watch the account manager
class Manager:
  def __init__ (self):
    self.am = am = Tp.AccountManager.dup()
    factory = am.get_factory()
    self.accounts = {}

    factory.add_contact_features ([Tp.ContactFeature.SUBSCRIPTION_STATES])
    am.connect ('account-removed', self.removed_cb )
    am.connect ('account-validity-changed', self.validity_changed_cb)
    am.prepare_async(None, self.prepared, None)


  def add_account (self, account):
    print "Adding account: " +  account.get_property ("display-name")
    self.accounts[account.get_property ("object-path")] = \
      Account (account)

  def remove_account (self, account):
    self.accounts.delete (account.get_property ("object-path"))

  def validity_changed_cb (self, am, account, valid):
    if valid:
        self.add_account (account)

  def removed_cb (self, am, account, valid):
    self.remove_account (account)

  def prepared (self, am, result, data):
    for a in am.get_valid_accounts():
        self.add_account (a)

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["datadir=", "rundir="])

        for o, a in opts:
            if o == "--datadir":
                setup_data_dir(a)
            elif o == "--rundir":
                setup_run_dir(a)
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    spawnbus ()

    Tp.debug_set_flags(os.getenv('PHOENIX_DEBUG', ''))

    loop = GObject.MainLoop()

    m = Manager()

    loop.run()
