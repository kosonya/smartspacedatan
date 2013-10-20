#!/usr/bin/env python

import numpy
import pickle
import matplotlib.pyplot as plt
import sys

import new_dataprocessor
import new_dataloader
import timeprocessor


group_by = 60


def prepare_for_plotting(arr, threshold=3):
	avg = numpy.average(arr)
	std = numpy.std(arr)
	res = []
	for x in arr:
		if abs(x - avg) > std*threshold:
			if x > avg:
				res.append(avg+std*threshold)
			else:
				res.append(avg-std*threshold)
		else:
			res.append(x)
	return res


class MaxMins(object):
	def __init__(self):
		self.mins = []
		self.maxes = []
	
	def add_feats(self, feats):
		if self.mins == []:
			self.mins = list(feats)
		else:
			for i in xrange(len(self.mins)):
				if feats[i] < self.mins[i]:
					self.mins[i] = feats[i]
		if self.maxes == []:
			self.maxes = list(feats)
		else:
			for i in xrange(len(self.maxes)):
				if feats[i] > self.maxes[i]:
					self.maxes[i] = feats[i]

	def get_maxes(self):
		return self.maxes

	def get_mins(self):
		return self.mins
def main():
	numpy.set_printoptions(precision=1, linewidth=284, threshold=40, edgeitems=13)
	filename2 = sys.argv[1]
	print "Loading PCA node from", filename2
	f = open(filename2,  "rb")
	pnode = pickle.load(f)
	f.close()
	print "Loading done"
	_min_t, _max_t = new_dataloader.get_min_max_timestamps()
	_min_t = timeprocessor.to_unixtime("2013-10-01 00:00:01")
	_max_t = timeprocessor.to_unixtime("2013-10-03 00:00:01")
	print "Minimum timestamp = %d (%s); maximum timestamp = %d (%s)" % (_min_t, timeprocessor.from_unixtime(_min_t), _max_t, timeprocessor.from_unixtime(_max_t))

	devices = new_dataloader.fetch_all_macs()
	#devices = ["17030002", "17030003"]
	print "Devices:", devices


	mm_raw = MaxMins()
	mm_pca = MaxMins()

	for t_start in xrange(_min_t, _max_t+1, group_by):
		t_end = t_start + group_by - 1
		for device in devices:
			print "Processing data from %s to %s (of %s through %s) from device %s" % (timeprocessor.from_unixtime(t_start), timeprocessor.from_unixtime(t_end), timeprocessor.from_unixtime(_min_t), timeprocessor.from_unixtime(_max_t), device)

			count, data = new_dataloader.load_data_bundle(t_start, t_end, device)
			if not data:
				print "No data, skipped"
			else:
				uz_data = new_dataprocessor.unzip_data_bundle(data)
				time_and_feats = new_dataprocessor.extract_all_features_from_sensors(uz_data)
				print time_and_feats
				_time, pols = new_dataprocessor.build_polynomial_features(time_and_feats, order=1)
				mm_raw.add_feats(pols[0])
				pca_feats = pnode.execute(pols)
				mm_pca.add_feats(pca_feats[0])
				
	raw_maxes = mm_raw.get_maxes()
	pca_maxes = mm_pca.get_maxes()
	raw_mins = mm_raw.get_mins()
	pca_mins = mm_pca.get_mins()
	plt.figure(1)
	plt.subplot(211)
	plt.bar(range(len(raw_maxes)), prepare_for_plotting(raw_maxes))
	plt.bar(range(len(raw_mins)), prepare_for_plotting(raw_mins))
	plt.subplot(212)
	plt.bar(range(len(pca_maxes)), prepare_for_plotting(pca_maxes))
	plt.bar(range(len(pca_mins)), prepare_for_plotting(pca_mins))
	plt.show()

if __name__ == "__main__":
	main()
