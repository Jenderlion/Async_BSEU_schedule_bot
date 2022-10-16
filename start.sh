#!/bin/bash

d=`dirname "$0 == sh"` fullpath=`cd "$d"; pwd`/`basename "$0"` dirpath=`cd "$d"; pwd`

cd $dirpath
source $dirpath/env/bin/activate
python $dirpath/bot/main.py "$@"
deactivate