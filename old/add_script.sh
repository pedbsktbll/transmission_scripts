#!/bin/bash

file=$1
path=$2
action=$3
LOGFILE="/etc/transmission-daemon/logs/add_script_log.txt"

echo $(date) >> $LOGFILE
echo "The file '$file' appeared in directory '$path' via '$action'" >> $LOGFILE
	
# First let's ensure it's a file
if [ ! -f "$path$file" ];
then
	echo "$path$file is NOT a file" >> $LOGFILE
	echo "" >> $LOGFILE
	exit
fi

# Now ensure it ends with .torrent
if [[ ! "$path$file" =~ \.torrent ]];
then
	echo "$path$file is NOT a torrent!" >> $LOGFILE
	echo "" >> $LOGFILE
	exit
fi

# yay we're a torrent! ADD ME!
echo "Adding $path$file to transmission-daemon!" >> $LOGFILE
echo "" >> $LOGFILE
transmission-remote --auth transmission -a "$path$file" -w "$path"
