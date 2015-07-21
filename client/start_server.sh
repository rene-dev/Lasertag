#!/bin/sh

cd "`dirname "$0"`"

export SDL_VIDEODRIVER=fbcon
export SDL_FBDEV=/dev/fb1
export SDL_NOMOUSE=1

exec python lasertag.py server $*
