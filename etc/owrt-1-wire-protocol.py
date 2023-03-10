#!/usr/bin/env python3
import os
import sys
import signal
import subprocess
from journal import journal

try:
    import ubus
except ImportError:
    journal.WriteLog("OWRT-1-wire-protocol", "Normal", "err", "Failed import ubus")
    sys.exit(-1)

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


def ubus_init():
    def get_1wire_list_callback(event, data):
        ret_val = {}
        lisst_dev = ['othel', 'test', 'Good']

        ret_val["unit"] = lisst_dev

        event.reply(ret_val)

    ubus.add(
        'owrt-1wire-dev', {
            'get_1wire_list': {
                'method': get_1wire_list_callback,
                'signature': {
                    'ubus_rpc_session': ubus.BLOBMSG_TYPE_STRING
                }
            }
        }
    )


if __name__ == '__main__':
    if not ubus.connect("/var/run/ubus.sock"):
        journal.WriteLog("OWRT-1-wire-protocol", "Normal", "err", "Failed connect to ubus")
        sys.exit(-1)

    try:
        result = subprocess.run(["owfs", "--fake=10,22", "-m", dir_owfs], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        journal.WriteLog("OWRT-1-wire-protocol", "Normal", "err", "Failed run OWFS")
        ubus.disconnect()
        sys.exit(-1)

    journal.WriteLog("OWRT-1-wire-protocol", "Normal", "notice", "Start module!")

    ubus_init()

    ret_val, list_1wire = get_list_1wire(dir_owfs)
    if ret_val:
        fl_run_main = False
    print(list_1wire)

    try:
        while fl_run_main:
            ubus.loop(1)
    except KeyboardInterrupt:
        pass
    finally:
        journal.WriteLog("OWRT-1-wire-protocol", "Normal", "notice", "Stop module!")

    subprocess.run(["killall", "owfs"])
    ubus.disconnect()
