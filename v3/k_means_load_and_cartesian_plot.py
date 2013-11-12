#!/usr/bin/env python

import numpy
import pickle
import matplotlib.pyplot as plt
import sys

import dataprovider

group_by = 60


def main():
    numpy.set_printoptions(precision=1, linewidth=284, threshold=40, edgeitems=13)

    X = []
    Y = []
    order = 2

    coeffs = raw_readings_norm_coeffs = {"temp": 100,
                                        "light": 100,
                                        "humidity" : 100, "pressure": 1e5, 
                                        "audio_p2p": 100, "motion" : 1}

    data_provider = dataprovider.DataProvider(order=order, debug=True,
                                                      start_time = 1379984887,
                                                      stop_time = 1379984887+3600*24*2,
                                                      device_list = ["17030002"],
                                                      eliminate_const_one=True, device_groupping="dict",
                                                  raw_readings_norm_coeffs = coeffs)
    f = open("2_order_knode.p", "rb")
    knode = pickle.load(f)
    f.close()
    

    for data in data_provider:
        print data
        t, d = data["17030002"]
        X.append(t)
        l = knode.label(d)[0]
        Y.append(l)


    plt.plot(X, Y, 'ro')
    plt.show()

if __name__ == "__main__":
    main()
