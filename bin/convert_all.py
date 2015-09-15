# -*- encoding: utf-8 -*-

import sys
import os
import xlrd
import collections
import uuid
import json

def parse_line(line_str):
    parsed = line_str.split("_")
    if len(parsed) == 2:
        return (int(parsed[0]), parsed[1])
    else:
        print "Invalid Line Expression."
        sys.exit(-1)

def parse_sheet(sheet, misc_data, stations, buses, lines, daytype):
    print "## Sheet: %s" % sheet.name

    # まずはStationsリストを作成
    start_index = -1
    end_index = -1

    line_stations = []

    # 駅データを取得
    for row in range(sheet.nrows):
        id_value = sheet.cell(row, 1).value
        str_value = sheet.cell(row, 2).value

        if (start_index == -1):
            if (str_value == ""):
                continue
            else:
                start_index = row
                id_value = "b_%s" % (int(id_value))
                line_stations.append(id_value)
                if (not id_value in stations):
                    station_info = misc_data["station_misc"][id_value]
                    stations[id_value] = {"name": str_value, "buses": [], "coord": station_info["coordinates"], "yomi": station_info["yomi"]}
                elif (stations[id_value]["name"] != str_value):
                    print "Invalid data!"
                    sys.exit(-1)
        else:
            if (str_value == ""):
                break
            else:
                end_index = row
                id_value = "b_%s" % int(id_value)
                line_stations.append(id_value)
                if (not id_value in stations):
                    station_info = misc_data["station_misc"][id_value]
                    stations[id_value] = {"name": str_value, "buses": [], "coord": station_info["coordinates"], "yomi": station_info["yomi"]}
                elif (stations[id_value]["name"] != str_value):
                    print "Invalid data!"
                    sys.exit(-1)

    print " -> %d stations has been detected.[%d, %d]" % (len(stations.keys()), start_index, end_index)

    (line_number, line_name) = parse_line(sheet.name)
    line_id = misc_data["lines"][daytype][sheet.name]

    if (not daytype in lines):
        lines[daytype] = {}

    # バス停/系統を検証
    if (not line_id in lines[daytype]):
        # 新規作成
        lines[daytype][line_id] = {"name": line_name, "number": line_number, "buses": [], "stations": line_stations}
    else:
        # 検証
        if (len(lines[daytype][line_id]["stations"]) != len(line_stations)):
            print "Invalid data.(Station count of line)"
            sys.exit(-1)

        for i in range(len(lines[daytype][line_id]["stations"])):
            if (lines[daytype][line_id]["stations"][i] != line_stations[i]):
                print "Invalid data. (Station order/data)"
                sys.exit(-1)

    # バスに着目
    count = 0
    for col in range(sheet.ncols):
        col_header = sheet.cell(1, col).value
        if (type(col_header) == float):
            count += 1
            bus_id = str(uuid.uuid4())
            print " * Reading: (Id: %s) Bus #%s in %s" % (bus_id, int(col_header), line_id)

            if not bus_id in buses:
                buses[bus_id] = {"line_id": line_id, "dept_times": [], "daytype": daytype}
            else:
                print "Duplicate BusId!"
                sys.exit(-1)

            lines[daytype][line_id]["buses"].append(bus_id)

            for row in range(start_index, end_index):
                staid_value = "b_%s" % int(sheet.cell(row, 1).value)
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
                    buses[bus_id]["dept_times"].append({"station_id": staid_value, "dept": time_value, "daytype": daytype})

    print " -> %d bus info has been parsed." % count

    return (stations, buses, lines)

def parse_book(filename, misc_data, stations, buses, lines, daytype):
    print "# Parsing : %s" % filename
    book = xlrd.open_workbook(filename)
    # Output book info
    print " * There are %d sheets in this book." % book.nsheets

    for index in range(book.nsheets):
        (stations, buses, lines) = parse_sheet(book.sheet_by_index(index), misc_data, stations, buses, lines, daytype)

    return (stations, buses, lines)
    # return {"stations": stations, "buses": buses, "types": types}

if __name__ == "__main__":
    args = sys.argv
    if (len(args) != 6):
        sys.stderr.write("Usage: python %s [Input Misc Data(*.json)] [Input *Weekday* file(*.xls)] [Input *Saturday* file(*.xls)] [Input *Holiday* file(*.xls) ][Output file(*.json)]\n" % args[0])
        sys.exit(-1)

    misc_data_path = args[1]
    input_weekday_path = args[2]
    input_satureday_path = args[3]
    input_holiday_path = args[4]
    output_path = args[5]

    misc_data = {}
    stations = {}
    buses = {}
    lines = {}

    lf = open(misc_data_path, "r")
    misc_data = json.load(lf)
    lf.close()

    (stations, buses, lines) = parse_book(input_weekday_path, misc_data, stations, buses, lines, "weekday")
    (stations, buses, lines) = parse_book(input_satureday_path, misc_data, stations, buses, lines, "saturday")
    (stations, buses, lines) = parse_book(input_holiday_path, misc_data, stations, buses, lines, "holiday")
    data = {"stations": stations, "buses": buses, "lines": lines}
    f = open(output_path, "w")
    f.write(json.dumps(data))
    f.close()

