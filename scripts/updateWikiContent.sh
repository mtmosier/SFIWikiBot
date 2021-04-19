#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON=/usr/bin/python3

echo `date` " - Begin galaxy data update" >> /home/app/app.log
echo Running updateWikiGalaxyContent.py
$PYTHON $DIR/updateWikiGalaxyContent.py
echo `date` " - End galaxy data update" >> /home/app/app.log

echo `date` " - Begin ship data update" >> /home/app/app.log
echo Running updateWikiShipContent.py
$PYTHON $DIR/updateWikiShipContent.py
echo `date` " - End ship data update" >> /home/app/app.log

echo `date` " - Begin item data update" >> /home/app/app.log
echo Running updateWikiItemContent.py
$PYTHON $DIR/updateWikiItemContent.py
echo `date` " - End item data update" >> /home/app/app.log

exit 0
