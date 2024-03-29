#!/usr/bin/env python

import sys
import os
import os.path
import shutil

def usage():
    print "copyall.py filename"

def parsefolder(folder):
    for i in os.listdir(folder):
        fullname = os.path.join(folder, i)
        if os.path.isdir(fullname):
            if os.path.isdir(SOURCE_FILE):
                pass
            else:
                shutil.copy(SOURCE_FILE, fullname)
            parsefolder(fullname)


if __name__ == "__main__":
    global SOURCE_FILE
    if len(sys.argv) < 2:
        usage()
    else:
        for i in sys.argv[1:]:
            SOURCE_FILE = i
            parsefolder('.')
