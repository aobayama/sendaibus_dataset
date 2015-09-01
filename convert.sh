#!/bin/bash

python bin/converter.py original/冊子型.xls json/bus_weekday.json
python bin/converter.py original/冊子型土曜.xls json/bus_saturday.json
python bin/converter.py original/冊子型休日.xls json/bus_holiday.json

python bin/convert_all.py original/冊子型.xls original/冊子型土曜.xls original/冊子型休日.xls json/bus_all.json

echo "Finished."

