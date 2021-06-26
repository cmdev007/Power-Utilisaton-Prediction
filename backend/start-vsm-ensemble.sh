#!/bin/bash

youtube-dl $1 -o - | ffmpeg -i - -f wav - | pv | python3.8 ./backend/sentiment-vsm-ensemble.py $2