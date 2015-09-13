#!/usr/bin/env ruby
# -*- coding: utf-8 -*-

# This code merges coords.json and yomigana.csv. it generates merged-busstop database
#
# If you want a readable json, execute below:
# $ cat coords_yomigana.json | ruby -r json -e 'jj(JSON.parse!(STDIN.read))''

require 'json'
require 'csv'

source_csv = "../csv/yomigana.csv"
# "busstop_name", "yomigana"
source_json = "../json/coords.json"
# { "unique_id" : { "coordinates" : {"lat": lat, "lon": lon}, "name": name}}
target_json = "../json/coords_yomigana.json"
# { "unique_id" : { "coordinates" : {"lat": lat, "lon": lon}, "name": name, "yomi": yomi}}

# ---------

dump_data   = Hash.new()
source_data = Hash.new()
target_data = Hash.new() # => merged data

CSV.foreach(source_csv, "r") do |row|
  dump_data.store(row[0],row[1])
end

open(source_json) do |io|
  source_data = JSON.load(io)
end

source_data.each do |key,val|
  target_data.store(
    key,
    {
      "coordinates" => val["coordinates"],
      "name"        => val["name"],
      "yomi"        => dump_data[val["name"]]
    }
  )
end

open(target_json, "w") do |io|
  JSON.dump(target_data, io)
end

