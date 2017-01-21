#!/bin/bash
ps -ef | grep key_event_writer | grep -v grep | awk '{print $2}' |xargs kill
cd /home/pi/Vision
/home/pi/.virtualenvs/cv/bin/python key_event_writer.py --conf conf.json
