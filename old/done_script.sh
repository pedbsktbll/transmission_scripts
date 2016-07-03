#!/bin/bash
# alias.sh

shopt -s expand_aliases
# Must set this option, else script will not expand aliases.

LOGFILE="/etc/transmission-daemon/logs/done_script_log.txt"
TORRENT_DIR="$TR_TORRENT_DIR$TR_TORRENT_NAME"
TEMP=${TR_TORRENT_DIR:15}
OUT_DIR="/data/$(echo $TEMP| cut -d '/' -f 1)/_queue/$TR_TORRENT_NAME"

alias fix_rars="unrar e -r"

echo $OUT_DIR
if [[ -z $TR_TORRENT_DIR ]]
then
   echo "ERROR! Running outside transmission-daemon context!"
   echo " -z error!" >> $LOGFILE
   exit
fi

echo $(date) >> $LOGFILE
echo $TORRENT_DIR >> $LOGFILE
echo $OUT_DIR >> $LOGFILE

if [[ -d $TORRENT_DIR ]]
then
   echo "TORRENT DIRECTORY detected" >> $LOGFILE
#   mkdir "$OUT_DIR"

    if [[ -n $(find "$TORRENT_DIR" -name *.rar) ]]
    then
      echo "RAR FILES found!" >> $LOGFILE
      mkdir "$OUT_DIR"
      fix_rars "$TORRENT_DIR/*.rar" "$OUT_DIR"
#      chgrp -R josh "$OUT_DIR"
      chmod 777 "$OUT_DIR"
      filebot -rename "$OUT_DIR"
    else
      echo "NO RAR FILES" >> $LOGFILE
      ln -s "$TORRENT_DIR/" "$OUT_DIR"
#      cp -r "$TORRENT_DIR/" "/data/queue/"
#      chgrp -R josh "$OUT_DIR"
      chmod 777 "$OUT_DIR"
      filebot -rename "$OUT_DIR"
   fi
else
   if [[ -f $TORRENT_DIR ]]
   then
      echo "Single TORRENT FILE detected" >> $LOGFILE
#      cp "$TORRENT_DIR" "$OUT_DIR"
       ln -s "$TORRENT_DIR" "$OUT_DIR"
#      chgrp -R josh "$OUT_DIR"
      chmod 777 "$OUT_DIR"
      filebot -rename "$OUT_DIR"
   fi
fi

echo "" >> $LOGFILE
