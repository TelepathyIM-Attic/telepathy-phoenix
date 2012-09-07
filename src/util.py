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
    (prefix, quiet) = u
    line = d.read_line_finish (r)
    if not quiet:
        print prefix + ": " + str(line)
    d.read_line_async (0, None, _got_line, u)

def _process_input(f, prefix, quiet):
    i = Gio.UnixInputStream.new (f.fileno(), True)
    d = Gio.DataInputStream.new (i)
    d.read_line_async (0, None, _got_line, (prefix, quiet))


def spawnbus(quiet = False):
    command = [ "dbus-daemon", "--session", "--nofork", "--print-address" ]

    process = subprocess.Popen (command,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    atexit.register (lambda p: os.kill (p.pid, signal.SIGKILL), process)

    address = process.stdout.readline().rstrip()
    os.environ ["DBUS_SESSION_BUS_ADDRESS"] = address
    if not quiet:
        print "Temporary Session bus: %s" % address

    # Process stdout
    _process_input (process.stdout, "STDOUT", quiet)
    _process_input (process.stderr, "STDERR", quiet)
    return process

def override_env (variable, var, quiet = False):
    os.environ[variable] = var
    if not quiet:
        print "Setting %s to %s" % (variable, var)

def prepend_env_path (variable, prefix, quiet = False):
    current = os.getenv(variable)
    if current != None:
        p = prefix + ":" + current
    else:
        p = prefix
    override_env (variable, p, quiet)

def setup_data_dir (path, quiet = False):
    # Define default if not set as per XDG spec
    if os.getenv("XDG_DATA_DIRS") == None:
        os.environ["XDG_DATA_DIRS"] = "/usr/local/share/:/usr/share/"
    prepend_env_path ("XDG_DATA_DIRS", path, quiet)

def setup_run_dir (path, quiet= False):
    # Setup all the various XDG paths
    override_env ("XDG_CONFIG_HOME", os.path.join (path, ".config"), quiet)
    override_env ("XDG_CACHE_HOME", os.path.join (path, ".cache"), quiet)
    override_env ("XDG_DATA_HOME", os.path.join (path, ".local"), quiet)
    override_env ("MC_ACCOUNT_DIR",
        os.path.join (path, ".config", "mission-control", "accounts"), quiet)

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
