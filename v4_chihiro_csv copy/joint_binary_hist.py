#!/usr/bin/env python

import dataloader
import dataprocessor
import numpy
import math
import pickle
import mdp
import itertools

def mul(seq):
	res = seq[0]
	if len(seq) == 1:
		return res
	for x in seq[1:]:
		res *= x
	return res

def build_feats(in_arr, order, debug = False):
	res = None
	i = 1
	in_arr = numpy.hstack( (numpy.ones([in_arr.shape[0], 1]), in_arr) )
	for feat in itertools.combinations_with_replacement(in_arr.T, r = order):
		if debug:
			print "Processing feature", i
		i += 1
		arr = mul(feat)
		arr = arr.reshape([arr.size, 1])
		if res == None:
			res = arr
		else:
			res = numpy.hstack( (res, arr) )
	res = res[:,1:]
	return res

def posts_to_fence(posts):
	return reduce(lambda (lst, prev), cur: (numpy.hstack( (lst, float(cur+prev)/2.0) ), cur), posts[1:], (numpy.array([]), posts[0]))[0]


def main():
	group_by = 120*1000
	order = 4
	interesting_features = [2, 6, 10, 18]
	#filename = "small_subset.110_readings.cal.csv.groupped_dataset_binary.p"
	filename = "decreased_zeros.110_readings.cal.csv.groupped_dataset_binary.p"
	f = open(filename, "rb")
	print "Locading data from", filename
	groupped_dataset = pickle.load(f)
	print "Loaded"
	f.close()
	groupped_data_subset = {}
	for people in groupped_dataset.keys():
		for feat_n in interesting_features:
			feat = groupped_dataset[people][:,feat_n]
			feat = feat.reshape( (feat.size, 1) )
			if groupped_data_subset.has_key(people):
				groupped_data_subset[people] = numpy.hstack( (groupped_data_subset[people], feat) )
			else:
				groupped_data_subset[people] = feat
			#print people, feat_n, feat
		print groupped_data_subset[people]
		
	stats = {}
	total = sum([x.shape[0] for x in groupped_data_subset.values()])
	nz_total = sum([x[1].shape[0] for x in groupped_data_subset.items() if x[0] != 0])
	print "Total:", total
	print "Total non-zeroes:", nz_total
	nbins = 10
	for npeople in groupped_data_subset.keys():
		stats[npeople] = {}
		stats[npeople]["marginal"] = float(groupped_data_subset[npeople].shape[0])/float(total)
		H, edges = numpy.histogramdd(groupped_data_subset[npeople], bins = nbins, normed = False)
		centers = map(posts_to_fence, edges)
		X = None
		Y = None
		for indices in itertools.product(xrange(nbins), repeat = len(interesting_features)):
			#print indices, [centers[i][indices[i]] for i in xrange(len(interesting_features))], H[indices]
			x = numpy.array([centers[i][indices[i]] for i in xrange(len(interesting_features))])
			y = numpy.array(H[indices])
			x = x.reshape( (1, x.size) )
			y = y.reshape( (1, 1) )
			if X == None:
				X = x
			else:
				X = numpy.vstack( (X, x) )
			if Y == None:
				Y = y
			else:
				Y = numpy.vstack( (Y, y) )

		Y = Y / numpy.max(Y)
		X = X / numpy.max(X)
		X_feats = build_feats(X, order = order)
		print ("%d:" % npeople)
		lnode = mdp.nodes.LinearRegressionNode(use_pinv = True)
		lnode.train(X_feats, Y)
		lnode.stop_training()
		stats[npeople]["lnode"] = lnode
		print X_feats
		print Y
		print "\n"
	#print X_feats[0] 

	rights = 0
	
	total_positives = 0
	true_positives = 0
	total_negatives = 0
	true_negatives = 0

	cur_total = 0
	previous_percent_done = 0
	report_step = 0.1

	for people_true in groupped_data_subset.keys():
		for reading in groupped_data_subset[people_true]:
			X = reading.reshape( (1, reading.size) )
			X = X / numpy.max(X)
			X = build_feats(X, order = order)
			#print X
			pdfs = {}
			for npeople in stats.keys():
				pdfs[npeople] = stats[npeople]["lnode"].execute(X) * stats[npeople]["marginal"]
			people_estimate = max(pdfs.items(), key = lambda x: x[1])[0]
			#print pdfs
			#print people_true, people_estimate
			if people_true == people_estimate:
				rights += 1
				if people_true == 0:
					total_negatives += 1
					true_negatives += 1
				else:
					total_positives += 1
					true_positives += 1
			elif people_true == 0:
				total_negatives += 1
			else:
				total_positives += 1
			

			cur_total += 1
			percent_done = 100*float(cur_total)/total
			percent_success = 100*float(rights)/cur_total
			if percent_done - previous_percent_done >= report_step:
				print "Processing reading {} of {} ({}% done). Success rate so far: {}%".format(cur_total, total, percent_done, percent_success)
				previous_percent_done = percent_done

	

		
	print "Total:", total, "rights:", rights, "(", 100*float(rights)/float(total), "%)"
	print "Positive ratio:", 100*float(total_positives)/float(total), "%; true positives:", 100*float(true_positives)/float(total_positives), "%"
	print "Negative ratio:", 100*float(total_negatives)/float(total), "%; true negatives:", 100*float(true_negatives)/float(total_negatives), "%"

	
	
if __name__ == "__main__":
	main()
