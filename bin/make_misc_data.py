# -*- encoding: utf-8 -*-

import sys
import os
import xlrd
import time
import collections
import uuid
import json

def parse_sheet(sheet, lines, daytype):
    line_key = sheet.name

    if (not daytype in lines):
        lines[daytype] = {}

    # バス停/系統を検証
    if (not line_key in lines[daytype]):
        # 新規作成
        line_id = str(uuid.uuid4())
        lines[daytype][line_key] = line_id
        print "***WARN*** NEW LINE ID IS GENERATED."

    return lines

def parse_book(filename, lines, daytype):
    print "# Parsing : %s" % filename
    book = xlrd.open_workbook(filename)
    # Output book info
    print " * There are %d sheets in this book." % book.nsheets

    for index in range(book.nsheets):
        lines = parse_sheet(book.sheet_by_index(index), lines, daytype)

    return lines
    # return {"stations": stations, "buses": buses, "types": types}

if __name__ == "__main__":
    args = sys.argv
    if (len(args) != 6):
        sys.stderr.write("Usage: python %s [Input *Weekday* file(*.xls)] [Input *Saturday* file(*.xls)] [Input *Holiday* file(*.xls)] [Input station misc file(*.json)] [In/Out Misc id file(*.json)]\n" % args[0])
        sys.exit(-1)

    input_weekday_path = args[1]
    input_satureday_path = args[2]
    input_holiday_path = args[3]
    stations_misc_path = args[4]
    in_out_path = args[5]

    lines = {}
    cf = open(stations_misc_path, "r")
    station_misc = json.load(cf)
    cf.close()

    if (os.path.exists(in_out_path)):
        lf = open(in_out_path, "r")
        temp = json.load(lf)
        lf.close()
        lines = temp["lines"]

    lines = parse_book(input_weekday_path, lines, "weekday")
    lines = parse_book(input_satureday_path, lines, "saturday")
    lines = parse_book(input_holiday_path, lines, "holiday")

    data = {"lines": lines, "station_misc": station_misc}

    f = open(in_out_path, "w")
    f.write(json.dumps(data))
    f.close()

    print "Waiting 5sec for confirmation."

    time.sleep(5)

