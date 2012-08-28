#!/usr/bin/env python

import subprocess
import atexit
import os
import signal
import dbus

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
        os.environ["XDG_DATA_DIRS"] = " /usr/local/share/:/usr/share/"
    prepend_env_path ("XDG_DATA_DIRS", path)

def setup_run_dir (path):
    # Setup all the various XDG paths
    override_env ("XDG_CONFIG_HOME", os.path.join (path, ".config"))
    override_env ("XDG_CACHE_HOME", os.path.join (path, ".cache"))
    override_env ("XDG_DATA_HOME", os.path.join (path, ".local"))
    override_env ("MC_ACCOUNT_DIR",
        os.path.join (path, ".config", "mission-control", "accounts"))
