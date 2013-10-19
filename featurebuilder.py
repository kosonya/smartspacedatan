#!/usr/bin/env python

import dataloader
import dataprocessor
import itertools
import numpy
import multiprocessing

def work( vs ):
	print "Processing", len(vs), "features of", len(vs[0]), "readings start"
	res = reduce(lambda x, y: x*numpy.array(y), vs, numpy.ones([1, len(vs[0])]))
	print "Processing", len(vs), "features of", len(vs[0]), "readings done"
	return res


class FeatureBuilderOneDevice(object):
	def __init__(self, sensors, device_id, start_date_time, end_date_time):
		self.sensors = sensors
		self.sdt = start_date_time
		self.edt = end_date_time
		self.device_id = device_id

	def load_one(self):
		dl = dataloader.DataLoader(sensors= self.sensors, device_id = self.device_id)
		dl.load_data(start_date_time = self.sdt , end_date_time = self.edt)
		return dl.raw_data()

	def process_one_device(self, all_var_modes = ["average", "maximum", "variance", "extremums", "average derivative", "average absolute derivative"], group_mode = "time", group_by = 20):
		self.dp = dataprocessor.DataProcessor(self.load_one())
		self.varrays = self.dp.extract_all_features(all_var_modes, group_mode, group_by = 20)

	def build_pol_features(self, order):
		self.pols = []
		print "Building polynomal features (device id =", self.device_id, "order =", order, ")"
		for vs in itertools.combinations_with_replacement(self.varrays, order):
			self.pols.append(reduce(lambda x, y: x*numpy.array(y), vs, numpy.ones([1, len(vs[0])])))
			print "Processing", len(vs), "features of", len(vs[0]), "readings done"
		print len(self.pols), "polynomal features built (device id =", self.device_id, "order =", order, ")"

	def process_one_device_parallel(self, all_var_modes = ["average", "maximum", "variance", "extremums", "average derivative", "average absolute derivative"], group_mode = "time", group_by = 20, pool_size = 6):
		self.dp = dataprocessor.DataProcessor(self.load_one())
		self.varrays = self.dp.extract_all_features_parallel(all_var_modes, group_mode, group_by, pool_size)


	def build_pol_features_parallel(self, order, pool_size = 6):
		print "Building polynomal features (device id =", self.device_id, "order =", order, ")"
		pool = multiprocessing.Pool(pool_size)
		self.pols = reduce(lambda x, y: x + [y], pool.map(work, itertools.combinations_with_replacement(self.varrays, order)), [])
		print len(self.pols), "polynomal features built (device id =", self.device_id, "order =", order, ")"
def main():
	fb = FeatureBuilderOneDevice(sensors = ["temp", "audio_p2p", "light", "humidity", "pressure", "motion"], device_id = 17000002, start_date_time = "2013-10-01 00:00:01", end_date_time = "2013-10-02 00:00:01")
	fb.process_one_device()
	fb.build_pol_features(order = 1)

if __name__ == "__main__":
	main()
