#!/bin/bash
CONSUME=/var/lib/docker/volumes/paperless_consume/_data
LOG=/var/log/nc-to-paperless.log
date >> $LOG
rclone move nextcloud:Dokumente/Eingang $CONSUME --min-age 5s >> $LOG 2>&1
echo done >> $LOG
