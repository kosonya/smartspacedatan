#!/usr/bin/env python

import new_dataloader
import pickle
import os.path
import new_dataloader
import new_dataprocessor



class DataProvider(object):
	def __init__(self, order=1, use_pca=False, pca_nodes_path=None, db_host="localhost", db_user="root", db_password="", db_name="andrew", device_list=None, start_time=None, stop_time=None, debug=False, group_by = 60, device_groupping = "dict", eliminate_const_one=False):
		self.debug = debug
		self.order = order
		self.use_pca = use_pca
		self.eliminate_const_one = eliminate_const_one
		self.pca_nodes_path = pca_nodes_path
		if self.use_pca and not self.pca_nodes_path:
			raise Exception("PCA is planned to be used, but PCA nodes path is not specified")
		self.pca_nodes_filename = os.path.join(self.pca_nodes_path, "%d_order_pnode.p" % self.order)
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

		if start_time and stop_time and device_list:
			self.start_time = start_time
			self.stop_time = stop_time
			self.device_list = device_list
		else:
			new_dataloader.mysql_user = self.db_user
			new_dataloader.mysql_password = self.db_password
			new_dataloader.mysql_host = self.db_host
			new_dataloader.mysql_db = self.db_name
			min_t, max_t = new_dataloader.get_min_max_timestamps()
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
				self.device_list = new_dataloader.fetch_all_macs()
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
		if self.device_groupping == "dict":
			res = {}
			if self.debug:
				print "Processing from", self._start_t, "to", self._end_t
			for device in self.device_list:
				if self.debug:
					print "Processing device", device
				new_dataloader.mysql_user = self.db_user
				new_dataloader.mysql_password = self.db_password
				new_dataloader.mysql_host = self.db_host
				new_dataloader.mysql_db = self.db_name
				count, data = new_dataloader.load_data_bundle(self._start_t, self._end_t, device)
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
				return self.next()
			else:
				for (device, data) in res.items():
					if self.debug:
						print "\nProcessing device", device
						print "Number of readings", len(data)
						print "Number of raw features:", len(data[0])-1
						print "Extracting features"
					uz_data = new_dataprocessor.unzip_data_bundle(data)
					time_and_feats = new_dataprocessor.extract_all_features_from_sensors(uz_data)
					if self.debug:
						print len(time_and_feats) - 1, "features extracted"
					if self.debug:
						print "Building polynomial features of order", self.order
					_time, pols = new_dataprocessor.build_polynomial_features(time_and_feats, order=self.order)
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
				return res
		



def main():
	dataprov = DataProvider(order=1, use_pca = True, pca_nodes_path="results/2013_10_20_22_svd_true", debug=True, start_time = 1379984887, stop_time = 1379985187, device_list = ["17030002", "17030003", "17030004"])
	for data in dataprov:
		for device, d in data.items():
				print device, d

if __name__ == "__main__":
	main()
