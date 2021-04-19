#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON=/usr/bin/python3

echo `date` " - Begin cache refresh $1" >> /home/app/cacheRefresh.log

if [[ "$1" == "" || "$1" == "gameData" ]] ; then
    echo Running refreshCacheMed.py
    $PYTHON $DIR/refreshCacheMed.py
fi
if [[ "$1" == "" || "$1" == "wikiData" ]] ; then
    echo Running refreshCacheShort.py
    $PYTHON $DIR/refreshCacheShort.py
fi

chown -R root:app /tmp
chmod -R +r,ug+w /tmp
find /tmp -type d -print0 | xargs -0 chmod g+s

# Change localhost:80 to the correct url where you have the site set up
curl "http://localhost:80/RefreshData" > /dev/null 2>&1

echo `date` " - End cache refresh $1" >> /home/app/cacheRefresh.log

exit 0
