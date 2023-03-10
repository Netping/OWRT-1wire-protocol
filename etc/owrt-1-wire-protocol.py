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


def get_list_1wire(dir_mnt):
    dev_1wire = []
    ret_val = 0
    try:
        with os.scandir(dir_mnt) as files:
            subdir = [file.name for file in files if file.is_dir()]
            for i in range(len(subdir)):
                dir_name = subdir[i].split(".")
                if len(dir_name) == 2:
                    try:
                        int(dir_name[0], 16)
                        int(dir_name[1], 16)
                        dev_1wire.append(subdir[i])
                    except ValueError:
                        pass
    except FileNotFoundError:
        journal.WriteLog("OWRT-1-wire-protocol", "Normal", "err", "Not found mount dir OWFS")
        ret_val = 1

    return ret_val, dev_1wire


if __name__ == '__main__':

    try:
        result = subprocess.run(["owfs", "--fake=10,22", "-m", dir_owfs], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        journal.WriteLog("OWRT-1-wire-protocol", "Normal", "err", "Failed run OWFS")
        sys.exit(-1)

    journal.WriteLog("OWRT-1-wire-protocol", "Normal", "notice", "Start module!")

    ret_val, list_1wire = get_list_1wire(dir_owfs)
    if ret_val:
        fl_run_main = False
    print(list_1wire)

    try:
        while fl_run_main:
            time.sleep(3)
    except KeyboardInterrupt:
        pass
    finally:
        journal.WriteLog("OWRT-1-wire-protocol", "Normal", "notice", "Stop module!")

    subprocess.run(["killall", "owfs"])
