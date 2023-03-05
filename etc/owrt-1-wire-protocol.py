#!/usr/bin/env python3
import os
import sys
import time         # TODO: check->delete
import signal
import subprocess

fl_run_main = True
dir_owfs = "/mnt/owfs/"


def stop_run(signum, frame):
    global fl_run_main
# TODO:    journal.WriteLog("OWRT-1-wire-protocol", "Normal", "notice", "Received termination signal!")
    fl_run_main = False


signal.signal(signal.SIGTERM, stop_run)


if __name__ == '__main__':
    try:
        result = subprocess.run(["owfs", "--fake=10,22", "-m", dir_owfs], check=True)
    except subprocess.CalledProcessError:
        # завершение с ошибкой
        # TODO: journal--error
        print("except CalledProcessError")
        sys.exit(-1)

#    list_dir = os.listdir(dir_owfs)
#    for name_dir in list_dir:
#        if os.path.isdir(name_dir):
#            print(name_dir)
    with os.scandir(dir_owfs) as files:
        subdir = [file.name for file in files if file.is_dir()]
    print(subdir)

    try:
        while fl_run_main:
            print("Vasya")
            time.sleep(3)
    except KeyboardInterrupt:
        pass
    finally:
# TODO:        journal.WriteLog("OWRT-1-wire-protocol", "Normal", "notice", "Stop module!")
        print("OWRT-1-wire-protocol -- Stop module!")

    subprocess.run(["killall", "owfs"])
    print("killall owfs")
