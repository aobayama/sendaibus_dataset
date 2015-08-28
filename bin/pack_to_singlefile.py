# -*- encoding: utf-8 -*-

import sys
import os
import xlrd
import collections
import uuid
import json

def parse_sheet(sheet, stations, buses, routes, daytype):
    print "## Sheet: %s" % sheet.name

    # まずはStationsリストを作成
    start_index = -1
    end_index = -1

    route_stations = []

    # 駅データを取得
    for row in range(sheet.nrows):
        id_value = sheet.cell(row, 1).value
        str_value = sheet.cell(row, 2).value

        if (start_index == -1):
            if (str_value == ""):
                continue
            else:
                start_index = row
                id_value = int(id_value)
                route_stations.append(id_value)
                if (not id_value in stations):
                    stations[id_value] = {"name": str_value, "buses": []}
                elif (stations[id_value]["name"] != str_value):
                    print "Invalid data!"
                    sys.exit(-1)
        else:
            if (str_value == ""):
                break
            else:
                end_index = row
                id_value = int(id_value)
                route_stations.append(id_value)
                if (not id_value in stations):
                    stations[id_value] = {"name": str_value, "buses": []}
                elif (stations[id_value]["name"] != str_value):
                    print "Invalid data!"
                    sys.exit(-1)

    print " -> %d stations has been detected.[%d, %d]" % (len(stations.keys()), start_index, end_index)

    # バス停/系統を検証
    if (not sheet.name in routes):
        # 新規作成
        routes[sheet.name] = {"buses": [], "stations": route_stations}
    else:
        # 検証
        pass


    # バスに着目
    count = 0
    for col in range(sheet.ncols):
        col_header = sheet.cell(1, col).value
        if (type(col_header) == float):
            count += 1
            bus_id = str(uuid.uuid1())
            print " * Reading: (Id: %s) Bus #%s in %s" % (bus_id, int(col_header), sheet.name)

            routes[sheet.name]["buses"].append({"bus_id": bus_id, "daytype": daytype})

            for row in range(start_index, end_index):
                staid_value = int(sheet.cell(row, 1).value)
                time_value = sheet.cell(row, col).value

                if (time_value == u"∥"):
                    # 通過、もしくは通らない
                    pass
                elif (time_value == u"…"):
                    # そもそも走っていない
                    pass
                else:
                    # 時刻
                    stations[staid_value]["buses"].append({"bus_id": bus_id, "dept": time_value, "daytype": daytype})
                    buses[bus_id].append({"station_id": staid_value, "dept": time_value, "daytype": daytype})

    print " -> %d bus info has been parsed." % count


    return (stations, buses, routes)

def parse_book(filename, stations, buses, routes, daytype):
    print "# Parsing : %s" % filename
    book = xlrd.open_workbook(filename)
    # Output book info
    print " * There are %d sheets in this book." % book.nsheets

    for index in range(book.nsheets):
        (stations, buses, routes) = parse_sheet(book.sheet_by_index(index), stations, buses, routes, daytype)

    return (stations, buses, routes)
    # return {"stations": stations, "buses": buses, "types": types}

if __name__ == "__main__":
    args = sys.argv
    if (len(args) != 5):
        sys.stderr.write("Usage: python %s [Input *Weekday* file(*.xls)] [Input *Saturday* file(*.xls)] [Input *Holiday* file(*.xls) ][Output file(*.json)]\n" % args[0])
        sys.exit(-1)

    input_weekday_path = args[1]
    input_satureday_path = args[2]
    input_holiday_path = args[3]
    output_path = args[4]

    stations = {}
    buses = collections.defaultdict(list)
    routes = {}

    (stations, buses, routes) = parse_book(input_weekday_path, stations, buses, routes, "weekday")
    (stations, buses, routes) = parse_book(input_satureday_path, stations, buses, routes, "saturday")
    (stations, buses, routes) = parse_book(input_holiday_path, stations, buses, routes, "holiday")
    data = {"stations": stations, "buses": buses, "routes": routes}
    f = open(output_path, "w")
    f.write(json.dumps(data))
    f.close()

