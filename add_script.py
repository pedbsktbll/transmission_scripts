import sys
import os
import datetime
from subprocess import call

def main():
    args = sys.argv
    if len(args) < 4:
        print("Syntax: python add_script.py file path action")
        sys.exit(1)

    # Program Vars
    file = args[2] + args[1]
    action = args[3]
    logfile = "/data/logs/add_script.txt"

    # Ensure it's a file with specific extension
    if not os.path.isfile(file) or not file.lower().endswith('.torrent'):
        sys.exit(2)

    # Write to log file and make system call
    with open(logfile, 'a+') as l:
#        l.write(datetime.datetime.now().strftime("%m/%d/%Y @ %H:%M:%S") + "\n")
        l.write(datetime.datetime.now().strftime("%c") + os.linesep)
        ret = call(["transmission-remote", "--auth", "transmission", "-a", file, "-w", args[2]])
        if ret != 0:
            l.write("Error adding " + file + " Error Code: %d" + os.linesep + os.linesep %(ret))
        else:
            l.write("Adding " + file + os.linesep + os.linesep)

if __name__ == '__main__':
    main()
