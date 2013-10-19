#!/usr/bin/env python

import featurebuilder
import numpy
import mdp
import pickle



def main():
	fb = featurebuilder.FeatureBuilderOneDevice(sensors = ["temp", "audio_p2p", "light", "humidity", "pressure", "motion"], device_id = 17000002, start_date_time = "2013-09-24 00:00:01", end_date_time = "2013-10-18 00:00:01")
	fb.process_one_device()
	fb.build_pol_features(order = 3)
	numpy.set_printoptions(precision=1, linewidth=284, threshold=40, edgeitems=13)
	dataset = fb.get_data_set()
	pnode = mdp.nodes.PCANode(svd=True)
	print "Start PCAing"
	step = 50
	for i in xrange(0, dataset.shape[0], step):
		j = i+step
		print "Processing readings", i, "through", j - 1, "of", dataset.shape[0], "(", dataset.shape[1], "features)"
		d = dataset[i:j]
		print d
		pnode.train(d)
	print "Stopping training"
	pnode.stop_training(debug = True)
	print "PCAing done"
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

if __name__ == "__main__":
	main()
