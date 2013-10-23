#!/usr/bin/env python

import numpy
import pickle
import matplotlib.pyplot as plt
import sys

import new_dataprocessor
import new_dataloader
import timeprocessor


group_by = 60


def prepare_for_plotting(arr, threshold=10, debug = False):
	avg = numpy.average(arr)
	std = numpy.std(arr)
	res = []
	for x in arr:
		if debug: print x, avg, std
		if abs(x - avg) > std*threshold:
			if x > avg:
				res.append(avg+std*threshold)
			else:
				res.append(avg-std*threshold)
		else:
			res.append(x)
		if debug: print "added:", res[-1], "\n"
	return res

def trim(arr, threshold=100):
	res = [x if abs(x) < threshold else threshold for x in arr]
	print arr, max(arr)
	print res, max(res)
	print ""
	return res

class DataStats(object):
	def __init__(self):
		self.history = []

	def add(self, arr):
		self.history.append(list(arr))

	def get_maxes(self):
		return numpy.amax(numpy.transpose(numpy.array(self.history)), axis=1)

	def get_mins(self):
		return numpy.amin(numpy.transpose(numpy.array(self.history)), axis=1)

	def get_avgs(self):
		res = []
		for arr in numpy.transpose(numpy.array(self.history)):
			res.append(numpy.average(arr))
		return res

	def get_stds(self):	#That's so wrong...
		res = []
		for arr in numpy.transpose(numpy.array(self.history)):
			res.append(numpy.std(arr))
		return res


def main():
	numpy.set_printoptions(precision=1, linewidth=284, threshold=40, edgeitems=13)
	filename2 = sys.argv[1]
	print "Loading PCA node from", filename2
	f = open(filename2,  "rb")
	pnode = pickle.load(f)
	f.close()
	print "Loading done"
	_min_t, _max_t = new_dataloader.get_min_max_timestamps()
	_min_t = timeprocessor.to_unixtime("2013-10-01 10:00:01")
	_max_t = timeprocessor.to_unixtime("2013-10-02 00:00:01")
	print "Minimum timestamp = %d (%s); maximum timestamp = %d (%s)" % (_min_t, timeprocessor.from_unixtime(_min_t), _max_t, timeprocessor.from_unixtime(_max_t))

	devices = new_dataloader.fetch_all_macs()
	devices = ["17030002", "17030003"]
	print "Devices:", devices


	st_raw = DataStats()
	st_pca = DataStats()

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
				_time, pols = new_dataprocessor.build_polynomial_features(time_and_feats, order=2)
				st_raw.add(pols[0])
				pca_feats = pnode.execute(pols)
				st_pca.add(pca_feats[0])
				
	plt.figure(1)

	plt.subplot(221)
	raw_maxes = st_raw.get_avgs()
	plt.title("No PCA - averages")
	plt.xlabel("Variable")
	plt.bar(range(len(raw_maxes)), raw_maxes)

	plt.subplot(222)
	raw_stds = st_raw.get_stds()
	plt.title("No PCA - stds")
	plt.xlabel("Variable")
	plt.bar(range(len(raw_stds)), raw_stds)


	plt.subplot(223)
	pca_maxes = st_pca.get_avgs()
	plt.title("With PCA - averages")
	plt.xlabel("Variable")
	plt.bar(range(len(pca_maxes)), pca_maxes)


	plt.subplot(224)
	pca_stds = st_pca.get_stds()[5:100]
	plt.title("With PCA - stds")
	plt.xlabel("Variable")
	plt.bar(range(len(pca_stds)), pca_stds)


	plt.tight_layout()

	plt.show()

if __name__ == "__main__":
	main()
