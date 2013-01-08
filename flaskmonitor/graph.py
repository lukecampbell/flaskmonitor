#!/usr/bin/env python
'''
@author Luke Campbell
@file flaskmonitor/graph.py
'''
import matplotlib
matplotlib.use('Agg')

import numpy as np
import StringIO

def scatter(v):
    import matplotlib.pyplot as plt
    imgdata = StringIO.StringIO()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(np.arange(len(v)), v)
    fig.savefig(imgdata, format='png')
    plt.close()
    imgdata.seek(0)
    plt = None
    return imgdata.read()


