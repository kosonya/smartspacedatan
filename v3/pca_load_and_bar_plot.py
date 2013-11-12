#!/usr/bin/env python

import numpy
import pickle
import matplotlib.pyplot as plt
import sys

import dataprovider

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

	st_raw = DataStats()
	st_pca = DataStats()

	coeffs = raw_readings_norm_coeffs = {"temp": 100,
                                        "light": 100,
                                        "humidity" : 100, "pressure": 1e5, 
                                        "audio_p2p": 100, "motion" : 1}

	data_provider = dataprovider.DataProvider(order=1, raw_readings_norm_coeffs = coeffs, device_list=["17010002", "17010003", "17010004"], start_time = 1379990887, stop_time=1379990887+3600*4/40, debug=True, eliminate_const_one=True, device_groupping="dict", use_pca=True, pca_nodes_path = "results/05_11_2013_1_order_svd_true/")

	for data in data_provider:
		for device, arr in data.items():
			st_pca.add(arr[1])

	data_provider = dataprovider.DataProvider(order=1, raw_readings_norm_coeffs = coeffs, device_list=["17010002", "17010003", "17010004"], start_time = 1379990887, stop_time=1379990887+3600*24/40, debug=True, eliminate_const_one=True, device_groupping="dict")

	for data in data_provider:
		for device, arr in data.items():
			st_raw.add(arr[1])
				
				
	fig = plt.figure(1)

	f221 = fig.add_subplot(221)
	raw_maxes = st_raw.get_avgs()
	f221.set_title("No PCA - averages")
	f221.set_xlabel("Variable")
	f221.plot(range(len(raw_maxes)), raw_maxes, 'ro')
	f221.set_yscale('log')

	plt.subplot(222)
	raw_stds = st_raw.get_stds()
	plt.title("No PCA - stds")
	plt.xlabel("Variable")
	plt.bar(range(len(raw_stds)), raw_stds)


	plt.subplot(223)
	pca_maxes = st_pca.get_avgs()
	plt.title("With PCA - averages")
	plt.xlabel("Variable")
	plt.plot(range(len(pca_maxes)), pca_maxes, 'ro')
	plt.yscale('log')


	plt.subplot(224)
	pca_stds = st_pca.get_stds()[5:100]
	plt.title("With PCA - stds")
	plt.xlabel("Variable")
	plt.bar(range(len(pca_stds)), pca_stds)


	plt.tight_layout()

	plt.show()

if __name__ == "__main__":
	main()
