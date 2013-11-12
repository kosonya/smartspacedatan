#!/usr/bin/env python

import time
import numpy
import mdp
import pickle
import traceback

import dataprovider


group_by = 60


def _main(order = 2, pnodefile = "knode.p"):
    global group_by
    report = ""
    coeffs = raw_readings_norm_coeffs = {"temp": 100,
                                        "light": 100,
                                        "humidity" : 100, "pressure": 1e5, 
                                        "audio_p2p": 100, "motion" : 1}
    try:
        numpy.set_printoptions(precision=1, linewidth=284, threshold=40, edgeitems=13)
        if True:
            data_provider = dataprovider.DataProvider(order=order, debug=True,
                                                      start_time = 1379984887,
                                                      stop_time = 1379984887+3600*24*10,
                                                      device_list = ["17030002"],
                                                      eliminate_const_one=True, device_groupping="numpy_matrix",
                                                  raw_readings_norm_coeffs = coeffs)
        else:
            data_provider = dataprovider.DataProvider(order=1, debug=True,
                                                  eliminate_const_one=True,
                                                  device_groupping="numpy_matrix",
                                                 raw_readings_norm_coeffs = coeffs)

        pnode = mdp.nodes.KMeansClassifier(num_clusters = 4)

        processing_time_start = time.asctime()
        processing_time_start_s = time.time()
        print "Processing has started:", processing_time_start
    except Exception:
        tr = traceback.format_exc().splitlines()
        for line in tr:
            report += line + "\n"
        return

    try:
        for data in data_provider:
            example_pols_in = data[0]
            example_pols_in = example_pols_in.reshape(1, example_pols_in.size)
            pnode.train(data)
            print "\n"

        processing_time_end = time.asctime()
        processing_time_end_s = time.time()
    except Exception:
        tr = traceback.format_exc().splitlines()
        for line in tr:
            report += line + "\n"

    try:

        print "Stopping training..."
        stopping_time_start = time.asctime()
        print stopping_time_start
        stopping_time_start_s = time.time()
        pnode.stop_training()
        stopping_time_end = time.asctime()
        stopping_time_end_s = time.time()
        print "Training stopped:", stopping_time_end

        print "Dumping K-means node with pickle to:", pnodefile
        f = open(pnodefile,  "wb")
        pickle.dump(pnode, f)
        f.close()
        print "Dumped successfully"

    except Exception:
        tr = traceback.format_exc().splitlines()
        for line in tr:
            report += line + "\n"

    try:

        report += "K-means Node was dumped to %s with pickle\n" % pnodefile

        report += "Processing started at:\t" + str(processing_time_start) + "\n"
        report += "Processing end at:\t" + str(processing_time_end) + "\n"
        report += "It took %d seconds" % (processing_time_end_s - processing_time_start_s) + "\n"
        report += "Stopping started at:\t" + str(stopping_time_start) + "\n"
        report += "Stopping stopped at:\t" + str(stopping_time_end) + "\n"
        report += "It took %d seconds" % (stopping_time_end_s - stopping_time_start_s) + "\n"
        report += "Total time elapsed:\t%d seconds" % (stopping_time_end_s - processing_time_start_s) + "\n" + "\n"
        report += "Polynomial order:\t" + str(order) + "\n"
    except Exception:
        tr = traceback.format_exc().splitlines()
        for line in tr:
            report += line + "\n"


    print report
    return report

def main():
   for order in [2]:
        print "%d order processing has started" % order
        report = _main(order = order, pnodefile = ("%d_order_knode.p" % order))
        print "%d order processing has stopped" % order
        f = open( ("%d_order_k_means_report.txt" % order), "w")
        f.write(report)
        f.close()
        print "Report is written to", ("%d_order_k_means_report.txt" % order)


if __name__ == "__main__":
    main()
