#!/usr/bin/env python

import time
import numpy
import mdp
import pickle
import traceback

import dataprovider


group_by = 60


def _main(order = 2, pnodefile = "pnode.p", testpairfile = "testpair.p"):
    global group_by
    report = ""
    coeffs = raw_readings_norm_coeffs = {"temp": 100,
                                        "light": 100,
                                        "humidity" : 100, "pressure": 1e5, 
                                        "audio_p2p": 100, "motion" : 1}
    try:
        numpy.set_printoptions(precision=1, linewidth=284, threshold=40, edgeitems=13)
        if True:
            data_provider = dataprovider.DataProvider(order=1, debug=True,
                                                      start_time = 1379984887,
                                                      stop_time = 1379984887+3600*24,
                                                      device_list = ["17030002", "17030003", "17030004"],
                                                      eliminate_const_one=True, device_groupping="numpy_matrix",
                                                  raw_readings_norm_coeffs = coeffs)
        else:
            data_provider = dataprovider.DataProvider(order=1, debug=True,
                                                  eliminate_const_one=True,
                                                  device_groupping="numpy_matrix",
                                                 raw_readings_norm_coeffs = coeffs)

        pnode = mdp.nodes.PCANode(svd=True)

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
        pnode.stop_training(debug = True)
        stopping_time_end = time.asctime()
        stopping_time_end_s = time.time()
        print "Training stopped:", stopping_time_end

        print "Dumping PCA node with pickle to:", pnodefile
        f = open(pnodefile,  "wb")
        pickle.dump(pnode, f)
        f.close()
        print "Dumped successfully"

        print "Test example:"
        print example_pols_in
        example_pols_out = pnode.execute(example_pols_in)
        print "Result:"
        print example_pols_out

        print "Dumping test pair with pickle to:", testpairfile
        f = open(testpairfile,  "wb")
        pickle.dump((example_pols_in, example_pols_out), f)
        f.close()
        print "Dumped successfully"
    except Exception:
        tr = traceback.format_exc().splitlines()
        for line in tr:
            report += line + "\n"

    try:
        report += "Test example:\n" + str(example_pols_in) + "\n"
        report += "Test result:\n" + str(example_pols_out) + "\n\n"

        report += "PCA Node was dumped to %s with pickle\n" % pnodefile
        report += "Test pair was dumped to %s with pickle\n\n" % testpairfile

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
   for order in [1]:
        print "%d order processing has started" % order
        report = _main(order = order, pnodefile = ("%d_order_pnode.p" % order), testpairfile = ("%d_order_testpair.p" % order))
        print "%d order processing has stopped" % order
        f = open( ("%d_order_report.txt" % order), "w")
        f.write(report)
        f.close()
        print "Report is written to", ("%d_order_report.txt" % order)


if __name__ == "__main__":
    main()
