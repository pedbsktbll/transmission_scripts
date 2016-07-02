import os
import done_script

dir = '/data/trackers_movies/'
#with open("files.txt", "w") as a:
for filename in os.listdir(dir):
    if '.torrent' not in filename:
#            a.write(dir + filename + os.linesep)
#            a.flush()
        done_script.main(dir + filename)
