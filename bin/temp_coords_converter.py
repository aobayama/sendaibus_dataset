# -*- encoding: utf-8 -*-

import sys
import os
import xlrd
import time
import collections
import uuid
import json

if __name__ == "__main__":
    args = sys.argv
    if (len(args) != 3):
        sys.stderr.write("Usage: python %s [Input coords file{*.json)] [Output coords file(*.json)]\n" % args[0])
        sys.exit(-1)

    input_path = args[1]
    output_path = args[2]

    cf = open(input_path, "r")
    data = json.load(cf)
    cf.close()

    newdata = {}
    for key,value in data.iteritems():
        newdata["b_%s" % key] = value

    f = open(output_path, "w")
    f.write(json.dumps(newdata))
    f.close()



