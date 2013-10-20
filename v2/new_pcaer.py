#!/usr/bin/env python

import time
import numpy

import new_dataprocessor
import new_dataloader
import timeprocessor


group_by = 30










def main():
	global group_by
	numpy.set_printoptions(precision=1, linewidth=284, threshold=40, edgeitems=13)
	_min_t, _max_t = new_dataloader.get_min_max_timestamps()
	_min_t = timeprocessor.to_unixtime("2013-10-16 00:00:01")
	_max_t = timeprocessor.to_unixtime("2013-10-16 00:40:01")
	print "Minimum timestamp = %d (%s); maximum timestamp = %d (%s)" % (_min_t, timeprocessor.from_unixtime(_min_t), _max_t, timeprocessor.from_unixtime(_max_t))

	devices = new_dataloader.fetch_all_macs()
	print "Devices:", devices

	total_readings = 0
	total_bundles = 0
	dev_stats = {}
	for device in devices:
		dev_stats[device] = [0, 0]

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

				_time, pols = new_dataprocessor.build_polynomial_features(time_and_feats)
				n_pol_feats = pols.size
				print "%d polynomial features created" % n_pol_feats
				print pols
			print "\n"

	processing_time_end = time.asctime()
	processing_time_end_s = time.time()
	print "Device stats:"
	for device in devices:
		print "Device %s: %d readings, %d bundles created" % (device, dev_stats[device][0], dev_stats[device][1])
	print "Total readings processed:\t", total_readings
	print "Total data bundles created:\t", total_bundles
	print "Readings were groupped by %d seconds" % group_by
	print "Data processed from %s to %s" % ( timeprocessor.from_unixtime(_min_t), timeprocessor.from_unixtime(_max_t) ), "\n"

	print "Processing started at:\t", processing_time_start
	print "Processing end at:\t", processing_time_end
	print "It took %d seconds" % (processing_time_end_s - processing_time_start_s), "\n"
	print "Raw features:\t\t", n_raw_feats
	print "Extracted features:\t", n_extr_feats
	print "Polynomial features:\t", n_pol_feats




if __name__ == "__main__":
	main()
