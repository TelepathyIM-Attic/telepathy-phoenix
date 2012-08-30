#!/usr/bin/env python

import subprocess
import atexit
import os
import sys
import signal
import dbus

from threading import Thread
from gi.repository import GLib, Gio
from gi.repository import TelepathyGLib as Tp


def _got_line (d, r, u):
    line = d.read_line_finish (r)
    print "STDOUT: " + str(line)
    d.read_line_async (0, None, _got_line, None)

def _process_input(f):
    i = Gio.UnixInputStream.new (f.fileno(), True)
    d = Gio.DataInputStream.new (i)
    d.read_line_async (0, None, _got_line, None)


def spawnbus(config = None):
    command = [ "dbus-daemon", "--session", "--nofork", "--print-address" ]
    if config:
        command.append("--config-file=config")

    process = subprocess.Popen (command,
        stdout = subprocess.PIPE,
    )
    atexit.register (lambda p: os.kill (p.pid, signal.SIGKILL), process)

    address = process.stdout.readline().rstrip()
    os.environ ["DBUS_SESSION_BUS_ADDRESS"] = address
    print "Temporary Session bus: %s" % address

    # Process stdout
    _process_input (process.stdout)

def override_env (variable, var):
    os.environ[variable] = var
    print "Setting %s to %s" % (variable, var)

def prepend_env_path (variable, prefix):
    current = os.getenv(variable)
    if current != None:
        p = prefix + ":" + current
    else:
        p = prefix
    override_env (variable, p)

def setup_data_dir (path):
    # Define default if not set as per XDG spec
    if os.getenv("XDG_DATA_DIRS") == None:
        os.environ["XDG_DATA_DIRS"] = "/usr/local/share/:/usr/share/"
    prepend_env_path ("XDG_DATA_DIRS", path)

def setup_run_dir (path):
    # Setup all the various XDG paths
    override_env ("XDG_CONFIG_HOME", os.path.join (path, ".config"))
    override_env ("XDG_CACHE_HOME", os.path.join (path, ".cache"))
    override_env ("XDG_DATA_HOME", os.path.join (path, ".local"))
    override_env ("MC_ACCOUNT_DIR",
        os.path.join (path, ".config", "mission-control", "accounts"))

def got_account_cb (o, r, password, func):
    account = o.create_account_finish (r)
    # Put the password in our credentials store
    try:
        os.makedirs (os.path.join (GLib.get_user_config_dir (), "phoenix"))
    except:
        pass
    authfile = os.path.join (GLib.get_user_config_dir (), "phoenix", "auth")
    f = open (authfile, "a+")
    f.write (account.get_path_suffix() + " " + password + "\n")

    func(account)

def create_account (am, cm, protocol, name, parameters, password, func):
    request = Tp.AccountRequest.new (am, cm, protocol, name)
    for k,v in parameters.items():
        request.set_parameter (k, v)

    request.create_account_async (
        lambda o, r, u: got_account_cb (o, r, password, func),
        None)
