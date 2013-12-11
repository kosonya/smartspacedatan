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
	order = 4
	nbins = 20
	#filename = "small_subset.110_readings.cal.csv.groupped_dataset_binary.p"
	filename = "129A_readings.cal.csv.groupped_dataset_binary.p"
	f = open(filename, "rb")
	print "Locading data from", filename
	groupped_dataset = pickle.load(f)
	print "Loaded"
	f.close()

	stats = {}
	total = sum([x.shape[0] for x in groupped_dataset.values()])
	nz_total = sum([x[1].shape[0] for x in groupped_dataset.items() if x[0] != 0])
	print "Total:", total
	print "Total non-zeroes:", nz_total

	norm_coeffs = numpy.max(groupped_dataset[0], axis=0)
	for i in groupped_dataset.keys():
		groupped_dataset[i] = groupped_dataset[i] / norm_coeffs

	print "Training"

	for npeople in groupped_dataset.keys():
		stats[npeople] = {}
		stats[npeople]["marginal"] = float(groupped_dataset[npeople].shape[0])/float(total)
		lnodes = []
		for n_feature in xrange(groupped_dataset[npeople].shape[1]):
			feat = groupped_dataset[npeople][:,n_feature]
			people = numpy.ones(feat.size) * npeople
			feat_dataset = numpy.hstack( (feat, people) )
			#print feat_dataset
			H, fedges, pedges = numpy.histogram2d(feat, people, bins = nbins, normed = False)
			fcenters = posts_to_fence(fedges)
			pcenters = posts_to_fence(pedges)
			#print H
			#print fcenters
			#print pcenters
			X = None
			Y = None
			for f_i in xrange(len(fcenters)):
				for p_i in xrange(len(pcenters)):
					#print fcenters[f_i], pcenters[p_i], H[f_i][p_i]
					x = numpy.array([fcenters[f_i], pcenters[p_i]])
					y = numpy.array(H[f_i][p_i])
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
			#print X
			#print Y
			lnode = mdp.nodes.LinearRegressionNode(use_pinv = True)
			X_feats = build_feats(X, order = order)
			#print X_feats
			lnode.train(X_feats, Y)
			lnode.stop_training()
			lnodes.append(lnode)
		stats[npeople]["lnodes"] = lnodes
	print "Training done"


	rights = 0
	
	total_positives = 0
	true_positives = 0
	total_negatives = 0
	true_negatives = 0

	cur_total = 0
	previous_percent_done = 0
	report_step = 0.1

	for people_true in groupped_dataset.keys():
		for reading in groupped_dataset[people_true]:
			#print X
			pdfs = {}
			for npeople in stats.keys():
				cur_pdf = 1.0
				for n_feat in xrange(len(reading)):
					X = numpy.array([reading[n_feat], npeople])
					X = X.reshape( (1, X.size) )
					X = build_feats(X, order=order)
					#print X
					cur_pdf *= stats[npeople]["lnodes"][n_feat].execute(X)

				pdfs[npeople] = cur_pdf * stats[npeople]["marginal"]
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
