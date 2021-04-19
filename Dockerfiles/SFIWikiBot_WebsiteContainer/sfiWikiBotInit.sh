#!/bin/bash

PYTHON=/usr/bin/python3

echo `date` " - Begin cache initialization" >> /home/app/app.log

OUT=`echo -e "from SFIWikiBotLib import ItemUtils\nfrom SFIWikiBotLib import ShipUtils\nfrom SFIWikiBotLib import GalaxyUtils\nfrom SFIWikiBotLib import SmallConstants\nprint('Complete')" | $PYTHON`

# Fix permissions on the cache directories
chown -R root:app /tmp
chmod -R +r,ug+w /tmp
find /tmp -type d -print0 | xargs -0 chmod g+s

# Change localhost:80 to the correct url where you have the site set up
curl "http://localhost:80/RefreshData" > /dev/null 2>&1

echo `date` " - End cache initialization" >> /home/app/app.log

while true; do sleep 2; done
