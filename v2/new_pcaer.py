#!/usr/bin/env python

import time
import numpy
import mdp
import pickle

import new_dataprocessor
import new_dataloader
import timeprocessor


group_by = 60










def main(order = 2, pnodefile = "pnode.p", testpairfile = "testpair.p"):
	global group_by
	numpy.set_printoptions(precision=1, linewidth=284, threshold=40, edgeitems=13)
	_min_t, _max_t = new_dataloader.get_min_max_timestamps()
	#_min_t = timeprocessor.to_unixtime("2013-10-16 00:00:01")
	#_max_t = timeprocessor.to_unixtime("2013-10-16 00:04:01")
	print "Minimum timestamp = %d (%s); maximum timestamp = %d (%s)" % (_min_t, timeprocessor.from_unixtime(_min_t), _max_t, timeprocessor.from_unixtime(_max_t))

	devices = new_dataloader.fetch_all_macs()
	devices = ["17030002", "17030003"]
	print "Devices:", devices

	total_readings = 0
	total_bundles = 0
	dev_stats = {}
	for device in devices:
		dev_stats[device] = [0, 0]

	pnode = mdp.nodes.PCANode(svd=True)

	processing_time_start = time.asctime()
	processing_time_start_s = time.time()



	for t_start in xrange(_min_t, _max_t+1, group_by):
		t_end = t_start + group_by - 1
		for device in devices:
			print "I've been working for %d seconds and still got no candy!" % (time.time() - processing_time_start_s)
			print "Processing data from %s to %s (of %s through %s) from device %s" % (timeprocessor.from_unixtime(t_start), timeprocessor.from_unixtime(t_end), timeprocessor.from_unixtime(_min_t), timeprocessor.from_unixtime(_max_t), device)

			count, data = new_dataloader.load_data_bundle(t_start, t_end, device)
			if not data:
				print "No data, skipped"
			else:
				total_readings += count
				total_bundles += 1
				dev_stats[device][0] += count
				dev_stats[device][1] += 1
				print "%d readings" % count

				uz_data = new_dataprocessor.unzip_data_bundle(data)
				n_raw_feats = len(uz_data) - 1
				print "%d raw features present" % n_raw_feats

				time_and_feats = new_dataprocessor.extract_all_features_from_sensors(uz_data)
				n_extr_feats = len(time_and_feats) - 1
				print "%d features extracted" % n_extr_feats

				_time, pols = new_dataprocessor.build_polynomial_features(time_and_feats, order=order)
				n_pol_feats = pols.size
				example_pols_in = pols
				print "%d polynomial features created" % n_pol_feats
				print pols
				print "Adding to PCA node..."
				pnode.train(pols)
				print "Added!"
			print "\n"

	processing_time_end = time.asctime()
	processing_time_end_s = time.time()

	print "Stopping training..."
	stopping_time_start = time.asctime()
	stopping_time_start_s = time.time()
	pnode.stop_training(debug = True)
	stopping_time_end = time.asctime()
	stopping_time_end_s = time.time()

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

	report = ""

	report += "Test example:\n" + str(example_pols_in) + "\n"
	report += "Test result:\n" + str(example_pols_out) + "\n\n"

	report += "PCA Node was dumped to %s with pickle\n" % pnodefile
	report += "Test pair was dumped to %s with pickle\n\n" % testpairfile

	report += "Device stats:" + "\n"
	for device in devices:
		report += "Device %s: %d readings, %d bundles created" % (device, dev_stats[device][0], dev_stats[device][1]) + "\n"
	report += "Total readings processed:\t" + str(total_readings) + "\n"
	report += "Total data bundles created:\t" + str(total_bundles) + "\n"
	report += "Readings were groupped by %d seconds" % group_by + "\n"
	report += "Data processed from %s to %s" % ( timeprocessor.from_unixtime(_min_t), timeprocessor.from_unixtime(_max_t) ) + "\n" + "\n"

	report += "Processing started at:\t" + str(processing_time_start) + "\n"
	report += "Processing end at:\t" + str(processing_time_end) + "\n"
	report += "It took %d seconds" % (processing_time_end_s - processing_time_start_s) + "\n"
	report += "Stopping started at:\t" + str(stopping_time_start) + "\n"
	report += "Stopping stopped at:\t" + str(stopping_time_end) + "\n"
	report += "It took %d seconds" % (stopping_time_end_s - stopping_time_start_s) + "\n"
	report += "Total time elapsed:\t%d seconds" % (stopping_time_end_s - processing_time_start_s) + "\n" + "\n"
	report += "Raw features:\t\t" + str(n_raw_feats) + "\n"
	report += "Extracted features:\t" + str(n_extr_feats) + "\n"
	report += "Polynomial features:\t" + str(n_pol_feats) + "\n"
	report += "Polynomial order:\t" + str(order) + "\n"

	print report
	return report




if __name__ == "__main__":
	for order in [1, 2, 3]:
		print "%d order processing has started" % order
		report = main(order = order, pnodefile = ("%d_order_pnode.p" % order), testpairfile = ("%d_order_testpair.p" % order))
		print "%d order processing has stopped" % order
		f = open( ("%d_order_report.txt" % order), "w")
		f.write(report)
		f.close()
		print "Report is written to", ("%d_order_report.txt" % order)
