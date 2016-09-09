import sys
import os
import datetime
import glob
import subprocess
from subprocess import call
import re

def main():
    args = sys.argv
    if len(args) < 2:
        print("Syntax: python done_script.py file")
        sys.exit(1)

    fullDir = args[1]
#    fullDir = string
    baseDir = "/data/"
    logfile = baseDir + "logs/done_script.txt"
    extensions = ('*.mkv', '*.avi', '*.mp4')
    files = []

    # If it's a directory then call unrar and find all files with "extensions"
    if( os.path.isdir(fullDir)):
        call(["unrar", "e", "-r", fullDir + "/*.rar", fullDir])
        for ext in extensions:
            files.extend(glob.glob(fullDir + "/" + ext))
    else:
        files = [fullDir]

    # So this might be a bug in python's glob.glob, BUTTT...
    # glob.glob("/data/trackers_movies/Son.of.Saul.2015.720p.BluRay.x264-PSYCHD[rarbg]/*.mkv") NO WORK
    # glob.glob("/data/trackers_movies/Son.of.Saul.2015.720p.BluRay.x264-PSYCHD[rarbg*/*.mkv") WORK???
    if not files:
        for ext in extensions:
            files.extend(glob.glob(fullDir[:-1] + "*/" + ext))

    # Now we determine whether it's a movie or TV show
    if fullDir[15] == 'm':
        movie = True
    else:
        movie = False

    with open(logfile, "a") as l:
        l.write("**********************************************" + os.linesep)
        l.write(datetime.datetime.now().strftime("%c") + os.linesep)
        l.write("**********************************************" + os.linesep)
        l.write("Processing directory " + fullDir + os.linesep)
        for file in files:
            l.write("Now processing: " + file + os.linesep)
            if "sample" in os.path.basename(file).lower():
                l.write("Contained 'sample', continuing to next file" + os.linesep)
                continue

            if movie:
                try:
                    FinalizeMovie(file, l)
                except Exception as e:
                    l.write("Failure renaming " + file + " Error: " + str(e) + os.linesep)
            else:
                try:
                    FinalizeShow(file, l)
                except Exception as e:
                    l.write("Failure renaming " + file + " Error " + str(e) + os.linesep)
#               os.symlink(fullDir, outdir)
            l.write(os.linesep)
        l.write(os.linesep)




# http://stackoverflow.com/questions/18340576/parsing-filenames-with-pythons-re-module
def FinalizeMovie(file, l):
    # Let's try to setup a symlink to the movie, renamed with filebot
    proc = subprocess.Popen(["filebot", "--log-file", "/data/logs/.filebot/logs/fb.log", "--action", "symlink", "--db", "TheMovieDB", "-rename", file, "--output", "/data/movies/"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait(timeout=60)
    l.write(proc.stdout.read().decode('utf-8').rstrip() + os.linesep)
    l.write(proc.stderr.read().decode('utf-8').rstrip() + os.linesep)
    ret = proc.returncode

    if ret != 0:
        # If that fails, then we'll try to be more specific
        m = parseM(os.path.basename(file))
        title = m[0][0].replace(".", " ")
        l.write("Retrying FileBot with " + title + os.linesep)
        proc = subprocess.Popen(["filebot", "--log-file", "/data/logs/.filebot/logs/fb.log", "--action", "symlink", "--db", "TheMovieDB", "-non-strict", "--q", title, "-rename", file, "--output", "/data/movies/"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait(timeout=60)
        l.write(proc.stdout.read().decode('utf-8').rstrip() + os.linesep)
        l.write(proc.stderr.read().decode('utf-8').rstrip() + os.linesep)
        ret = proc.returncode

    l.write("retcode: " + str(ret) + os.linesep)
    if ret == 0:
        l.write("Success!" + os.linesep)
    else:
        raise Exception("Failed Parsing Movie")




def FinalizeShow(file, l):
    # Let's try to setup a symlink to the show, renamed with filebot
    s = parseS(os.path.basename(file))
    title = s[0][0].replace(".", " ")
    season = str(int(s[0][1]))
    episode = str(int(s[0][2]))
    outdir = "/data/shows/" + title + "/Season " + str(season) + "/"

    proc = subprocess.Popen(["filebot", "--log-file", "/data/logs/.filebot/logs/fb.log", "--action", "symlink", "--db", "TheTVDB", "-rename", file, "--output", outdir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait(timeout=60)
    l.write(proc.stdout.read().decode('utf-8').rstrip() + os.linesep)
    l.write(proc.stderr.read().decode('utf-8').rstrip() + os.linesep)
    ret = proc.returncode

    if ret != 0:
        # If that fails, then we'll try to be more specific
        l.write("Retrying FileBot with Title: " + title + " Season: " + season + " episode: " + episode + os.linesep)
        proc = subprocess.Popen(["filebot", "--log-file", "/data/logs/.filebot/logs/fb.log", "--action", "symlink", "--db", "TheTVDB", "-non-strict", "--q", title, "--filter", '"s == ' + season + ' && e == ' + episode + '"', "-rename", file, "--output", outdir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait(timeout=60)
        l.write(proc.stdout.read().decode('utf-8').rstrip() + os.linesep)
        l.write(proc.stderr.read().decode('utf-8').rstrip() + os.linesep)
        ret = proc.returncode

    l.write("retcode: " + str(ret) + os.linesep)
    if ret == 0:
        l.write("Success!" + os.linesep)
    else:
        raise Exception("Failed Parsing Movie")




def parseM(file):
    return re.findall(r"""(.*?[ .]\d{4})  # Title including year
        [ .a-zA-Z]*     # Space, period, or words
        (\d{3,4}p)?      # Quality
     """, file, re.VERBOSE)   




def parseS(file):
    ret = re.findall(r"""(.*)          # Title
        [ .]
        [Ss|season](\d{1,2})    # Season
        [Ee|episode](\d{1,2})    # Episode
        [ .a-zA-Z]*  # Space, period, or words like PROPER/Buried
        (\d{3,4}p)?   # Quality
    """, file, re.VERBOSE)

    if len(ret) > 0 and len(ret[0]) >= 3:
        return ret

    ret = re.findall(r"""(.*) # Title
        [ .]
        (?:
        (\d)(\d{2})\D          # This matches: outlander.112.hdtv-lol.mp4
        |(\d{1,2})x?(\d{1,2}))   # This matches: outlander.1112.hdtv-lol.mp4 AND American Dad! - 12x04 - Big Stan on Campus.mkv
#        |[Ss|season|(\d{1,2})](\d{1,2})[Ee|episode|x](\d{1,2})) # This matches everything else (hopefully)
        [ .a-zA-Z]*             # Space, period, or words like PROPER/Buried
        (\d{3,4}p)?             # Quality
        """, file, re.VERBOSE)


    title = ret[0][0]
    if title.endswith("-"):
        title = title[:-1] 
    if len(ret[0][1]) == 0:
        ret[0] = [ret[0][0], ret[0][3], ret[0][4], ret[0][5]]
    else:
        ret[0] = [ret[0][0], ret[0][1], ret[0][2], ret[0][5]]
    return ret


if __name__ == '__main__':
    main()
