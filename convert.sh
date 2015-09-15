#!/bin/bash

python bin/make_misc_data.py original/冊子型.xls original/冊子型土曜.xls original/冊子型休日.xls json/coords_yomigana.json json/bus_misc_data.json 

python bin/convert_all.py json/bus_misc_data.json original/冊子型.xls original/冊子型土曜.xls original/冊子型休日.xls json/bus_all.json

echo "Finished."

