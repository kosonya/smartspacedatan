#!/usr/bin/env python

import dataloader
import pickle
import os.path
import dataloader
import dataprocessor
import numpy



class DataProvider(object):
	def __init__(self, order=1, use_pca=False, pca_nodes_path=None, db_host="localhost", db_user="root", db_password="", db_name="andrew", device_list=None, start_time=None, stop_time=None, debug=False, group_by = 60, device_groupping = "dict", eliminate_const_one=True, dtype="float64"):
		self.debug = debug
		self.order = order
		self.dtype = dtype
		self.use_pca = use_pca
		self.eliminate_const_one = eliminate_const_one
		self.pca_nodes_path = pca_nodes_path
		if self.use_pca and not self.pca_nodes_path:
			raise Exception("PCA is planned to be used, but PCA nodes path is not specified")
		if pca_nodes_path:
			self.pca_nodes_filename = os.path.join(self.pca_nodes_path, "%d_order_pnode.p" % self.order)
		else:
			self.pca_nodes_filename = None
		if self.use_pca:
			if debug:
				print "Loading PCA node from", self.pca_nodes_filename
			f = open(self.pca_nodes_filename, "rb")
			self.pnode = pickle.load(f)
			f.close()
			if debug:
				print "Loading PCA node done"
		self.db_host = db_host
		self.db_user = db_user
		self.db_password = db_password
		self.db_name = db_name
		self.data_loader = dataloader.DataLoader(mysql_user = self.db_user, mysql_password = self.db_password, mysql_host = self.db_host, mysql_db = self.db_name)


		if start_time and stop_time and device_list:
			self.start_time = start_time
			self.stop_time = stop_time
			self.device_list = device_list
		else:
			min_t, max_t = self.data_loader.get_min_max_timestamps()
			if not start_time:
				self.start_time = min_t
				if debug:
					print "Start time not specified, using %d instead" % self.start_time
			else:
				self.start_time = start_time
			if not stop_time:
				self.stop_time = max_t
				if debug:
					print "Stop time not specified, using %d instead" % self.stop_time
			else:
				self.stop_time = stop_time
			if not device_list:
				self.device_list = self.data_loader.fetch_all_macs()
				if debug:
					print "Device list not specified, using all available instad:"
					for device in self.device_list:
						print "\t", device
			else:
				self.device_list = device_list
		self.group_by = group_by
		self.device_groupping = device_groupping
		self._start_t = self.start_time
		self._end_t = self.start_time + self.group_by

	def __iter__(self):
		return self

	def next(self):
		if self._end_t >= self.stop_time:
			raise StopIteration
		res = {}
		while not res:
			if self.debug:
				_t = (self._start_t + self._end_t)/2.0
				percent = 100.0 * (_t - self.start_time)/float((self.stop_time - self.start_time))
				print "Processing from", self._start_t, "to", self._end_t, "(", percent, " % done)"
			for device in self.device_list:
				if self.debug:
					print "Processing device", device
				count, data = self.data_loader.load_data_bundle(self._start_t, self._end_t, device)
				if count > 0:
					res[device] = data
					if self.debug:
						print "Loaded", count, "readings"
				elif self.debug:
					print "No data, skipped"
			if not res:
				if self.debug:
					print "No data at all, skipping"
				self._start_t = self._end_t
				self._end_t = self._start_t + self.group_by
				if self._end_t >= self.stop_time:
					raise StopIteration
		for (device, data) in res.items():
			if self.debug:
				print "\nProcessing device", device
				print "Number of readings", len(data)
				print "Number of raw features:", len(data[0])-1
				print "Extracting features"
			uz_data = dataprocessor.unzip_data_bundle(data)
			time_and_feats = dataprocessor.extract_all_features_from_sensors(uz_data)
			if self.debug:
				print len(time_and_feats) - 1, "features extracted"
			if self.debug:
				print "Building polynomial features of order", self.order
			_time, pols = dataprocessor.build_polynomial_features(time_and_feats, order=self.order)
			if self.eliminate_const_one:
				pols = pols[:,1:]
				if self.debug:
					print "Eliminating constant 1 from features"
			n_pol_feats = pols.size
			if self.debug:
				print "%d polynomial features created" % n_pol_feats
			res[device] = _time, pols
			if self.use_pca:
				if self.debug:
					print "Applying PCA"
				res[device] = _time, self.pnode.execute(res[device][1])
		self._start_t = self._end_t
		self._end_t = self._start_t + self.group_by
	
		if self.device_groupping == "dict":
			return res
		elif self.device_groupping == "numpy_matrix":
			arr = numpy.empty([len(res), n_pol_feats], dtype=self.dtype)
			for i in xrange(len(res)):
				arr[i] = res.values()[i][1][0]
			return arr
		



def main():
	numpy.set_printoptions(precision=1, linewidth=120, threshold=20, edgeitems=5)
	dataprov = DataProvider(order=1, use_pca = False, pca_nodes_path="../v2/results/2013_10_20_22_svd_true", debug=True, start_time = 1379984887, stop_time = 1379985187, device_list = ["17030002", "17030003", "17030004"], eliminate_const_one=True, device_groupping="numpy_matrix")
	for data in dataprov:
		if False:
			for device, d in data.items():
					print device, d
		print data

if __name__ == "__main__":
	main()
