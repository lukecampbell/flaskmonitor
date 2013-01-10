#!/usr/bin/env python
'''
@author Christopher Mueller
@file flaskmonitor/log_dump.py
'''
import csv

import StringIO

def log_dump(data):
    sf = StringIO.StringIO()
    writer = csv.writer(sf)
    vals = data['values']
    for x in vals:
        writer.writerow(x)

    sf.seek(0)
    return sf.read()
