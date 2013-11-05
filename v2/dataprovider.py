#!/usr/bin/env python

import new_dataloader
import pickle
import os.path
import new_dataloader

class DataProvider(object):
	def __init__(self, order=1, use_pca=False, pca_nodes_path=None, db_host="localhost", db_user="root", db_password="", db_name="andrew", device_list=None, start_time=None, stop_time=None, debug=False, group_by = 60, device_groupping = "all_list"):
		self.debug = debug
		self.order = order
		self.use_pca = use_pca
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
			if not stop_time:
				self.stop_time = max_t
				if debug:
					print "Stop time not specified, using %d instead" % self.stop_time
			if not device_list:
				self.device_list = new_dataloader.fetch_all_macs()
				if debug:
					print "Device list not specified, using all available instad:"
					for device in self.device_list:
						print "\t", device
		self.group_by = group_by
		self.device_groupping = device_groupping
		self._start_t = self.start_time
		self._end_t = self.start_time + self.group_by

	def __iter__(self):
		return self

	def next(self):
		if self._end_t >= self.stop_time:
			raise StopIteration
		if self.device_groupping == "all_list":
			res = []
			if self.debug:
				print "Processing from", self._start_t, "to", self._end_t
			for device in self.device_list:
				if self.debug:
					print "Processing device", device
				new_dataloader.mysql_user = self.db_user
				new_dataloader.mysql_password = self.db_password
				new_dataloader.mysql_host = self.db_host
				new_dataloader.mysql_db = self.db_name
				count, data = new_dataloader.load_data_bundle(self._start_t, self.stop_t, device)
				if count > 0:
					res += data
					print "Loaded", count, "readings"
				elif self.debug:
					print "No data, skipped"
			if not res:
				if debug:
					print "No data at all, skipping"
				self._start_t = self._end_t
				self._end_t = self._start_t + self.group_by
				return self.next()
			else:
				pass
			
				



def main():
	dataprov = DataProvider(order=1, use_pca = True, pca_nodes_path="results/2013_10_20_23_svd_true", debug=True)

if __name__ == "__main__":
	main()
