#!/usr/bin/env python

import featurebuilder
import numpy
import mdp
import pickle
import time



def main():
	t_start = time.asctime(time.localtime())
	print "Start:", t_start
	fb = featurebuilder.FeatureBuilderOneDevice(sensors = ["temp", "audio_p2p", "light", "humidity", "pressure", "motion"], device_id = 17000002, start_date_time = "2013-09-24 00:00:01", end_date_time = "2013-10-17 00:00:01")
	fb.process_one_device(all_var_modes = ["average", "maximum", "variance", "extremums", "average absolute derivative"])
	t_processed = time.asctime(time.localtime())
	print t_processed
	fb.build_pol_features(order = 3)
	t_built = time.asctime(time.localtime())
	print t_built
	numpy.set_printoptions(precision=1, linewidth=284, threshold=40, edgeitems=13)
	dataset = fb.get_data_set()
	pnode = mdp.nodes.PCANode(svd=True)
	print "Start PCAing"
	t_pca_start = time.asctime(time.localtime())
	print t_pca_start
	step = 100
	if step == 1:
		for i in xrange(dataset.shape[0]):
			print "Processing reading", i, "of", dataset.shape[0], "(", dataset.shape[1], "features)"
			d = dataset[i].reshape(1, dataset[i].size)
			print d
			pnode.train(d)
	else:
		for i in xrange(0, dataset.shape[0], step):
			j = i+step
			print "Processing readings", i, "through", j - 1, "of", dataset.shape[0], "(", dataset.shape[1], "features)"
			d = dataset[i:j]
			print d
			pnode.train(d)
	print "Stopping training"
	t_pca_stop = time.asctime(time.localtime())
	print t_pca_stop
	pnode.stop_training(debug = True)
	print "PCAing done"
	t_training_stop = time.asctime(time.localtime())
	print t_training_stop
	filename1 = "pca_output.bin"
	filename2 = "pnode.p"
	print "Saving PCA values to", filename1, "and", filename2
	pnode.save(filename1)
	f = open(filename2,  "wb")
	pickle.dump(pnode, f)
	f.close()
	print "Saving done"
	testin = dataset[0].reshape(1, dataset[0].size)
	print "Test in:"
	print testin
	testout = pnode.execute(testin)
	print "Testout:"
	print testout
	filename3 = "testpair.p"
	print "Saving test pair to", filename3
	f = open(filename3,  "wb")
	pickle.dump((testin, testout), f)
	f.close()
	print "Start:", t_start
	print "Print data loaded and features extracted:", t_processed
	print "Polynomial features built:", t_built
	print "PCA start:", t_pca_start
	print "PCA stop:", t_pca_stop
	print "PCA training stop:", t_training_stop
	print "Data set shape:", dataset.shape

if __name__ == "__main__":
	main()
