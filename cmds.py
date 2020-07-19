# ******************************************************************
# This file illustrates how to execute a command and get it's output
# ******************************************************************

import subprocess

for line in subprocess.getstatusoutput('ls -l'):
    print(line)
