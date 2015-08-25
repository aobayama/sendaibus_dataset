# -*- encoding: utf-8 -*-

import sys
import os
import xlrd
import collections
import uuid
import json

def parse_bus(col,sheet):
    pass

def parse_sheet(sheet, stations):
    print "## Sheet: %s" % sheet.name

    stations = {}
    buses = collections.defaultdict(list)

    # まずはStationsリストを作成
    start_index = -1
    end_index = -1

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
                if (not id_value in stations):
                    stations[id_value] = {"name": str_value, "buses": []}
        else:
            if (str_value == ""):
                break
            else:
                end_index = row
                id_value = int(id_value)
                if (not id_value in stations):
                    stations[id_value] = {"name": str_value, "buses": []}

    print " -> %d stations has been detected.[%d, %d]" % (len(stations.keys()), start_index, end_index)

    # バスに着目
    for col in range(sheet.ncols):
        col_header = sheet.cell(1, col).value
        if (type(col_header) == float):
            bus_id = str(uuid.uuid1())
            print " * Reading: (Id: %s) Bus #%s in %s" % (bus_id, int(col_header), sheet.name)

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
                    stations[staid_value]["buses"].append({"bus_id": bus_id, "dept": time_value})
                    buses[bus_id].append({"station_id": staid_value, "dept": time_value})

    print " -> %d bus info has been parsed." % len(buses.keys())

    return (sheet.name, stations, buses)

def parse_book(filename):
    print "# Parsing : %s" % filename
    book = xlrd.open_workbook(filename)
    # Output book info
    print " * There are %d sheets in this book." % book.nsheets

    stations = {}
    buses = {}
    types = {}

    for index in range(book.nsheets):
        (res_type, stations, res_buses) = parse_sheet(book.sheet_by_index(index), stations)
        buses.update(res_buses)

        if (res_type in types):
            print "Invalid data."
        else:
            types[res_type] = [x for x in res_buses.keys()]

    return {"stations": stations, "buses": buses, "types": types}

if __name__ == "__main__":
    args = sys.argv
    if (len(args) != 3):
        sys.stderr.write("Usage: python %s [Input file(*.xls)] [Output file(*.json)]\n" % args[0])
        sys.exit(-1)

    input_path = args[1]
    output_path = args[2]

    result = parse_book(input_path)
    f = open(output_path, "w")
    f.write(json.dumps(result))
    f.close()

