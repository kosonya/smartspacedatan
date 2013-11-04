#!/usr/bin/env python

import new_dataloader
import pickle
import os.path

class DataProvider(object):
	def __init__(self, order=1, use_pca=False, pca_nodes_path=None, db_host="localhost", db_user="root", db_password="", db_name="andrew", device_list=None, start_time=None, stop_time=None, debug=False):
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


def main():
	dataprov = DataProvider(use_pca = True, pca_nodes_path="results/2013_10_20_23_svd_true", debug=True)

if __name__ == "__main__":
	main()
