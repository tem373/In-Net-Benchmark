#! /usr/local/bin/python

import sys
label = sys.argv[1]

for line in sys.stdin:
  if str(line[0]) == label:
    records=line.split(", ")
    records=records[1:] # throw away first element
    for i in range(0, len(records)):
      print(i, records[i])
