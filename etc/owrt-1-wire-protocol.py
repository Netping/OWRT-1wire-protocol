#!/usr/bin/env python3
import os
import sys
import time         # TODO: check->delete
import signal
import subprocess
from journal import journal

fl_run_main = True
dir_owfs = "/mnt/owfs/"


def stop_run(signum, frame):
    global fl_run_main
    journal.WriteLog("OWRT-1-wire-protocol", "Normal", "notice", "Received termination signal!")
    fl_run_main = False


signal.signal(signal.SIGTERM, stop_run)


if __name__ == '__main__':

    try:
        result = subprocess.run(["owfs", "--fake=10,22", "-m", dir_owfs], check=True)
    except subprocess.CalledProcessError:
        journal.WriteLog("OWRT-1-wire-protocol", "Normal", "err", "Failed run OWFS")
        sys.exit(-1)

    journal.WriteLog("OWRT-1-wire-protocol", "Normal", "notice", "Start module!")

#    list_dir = os.listdir(dir_owfs)
#    for name_dir in list_dir:
#        if os.path.isdir(name_dir):
#            print(name_dir)
    with os.scandir(dir_owfs) as files:
        subdir = [file.name for file in files if file.is_dir()]
    print(subdir)

    try:
        while fl_run_main:
            time.sleep(3)
    except KeyboardInterrupt:
        pass
    finally:
        journal.WriteLog("OWRT-1-wire-protocol", "Normal", "notice", "Stop module!")

    subprocess.run(["killall", "owfs"])
