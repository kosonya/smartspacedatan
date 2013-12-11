#!/usr/bin/env python

import numpy
import pickle
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


def main():
	group_by = 120*1000
	order = 1
	filename = "110_readings.cal.csv.matrix_dataset_binary.p"
	#filename = "decreased_zeros.110_readings.cal.csv.matrix_dataset_rounded.p"
	f = open(filename, "rb")
	dataset = pickle.load(f)
	f.close()
	
	maxes = numpy.max(dataset, axis=0)
	maxes[-1] = 1
	dataset = dataset / maxes

	people = dataset[:,dataset.shape[1]-1]

	print dataset
	print dataset.shape

	print people
	
	corrs = []

	for i in xrange(dataset.shape[1]):
		#print i, numpy.corrcoef(people, dataset[:,i])[0][1]#, numpy.cov(numpy.vstack( (people, dataset[:,i]) ) )
		#corrs.append( (i, numpy.correlate(people, dataset[:,i], old_behavior = True)) )
		corrs.append( (i, numpy.linalg.det(numpy.cov(people, dataset[:,i]))))
		print numpy.linalg.det(numpy.cov(people, dataset[:,i]))


	for i, corr in sorted(corrs[:-1], key=lambda x: -abs(x[1])):
		print i, corr

	print "\n\n\nPolynomial features"

	feats = dataset[:,:dataset.shape[1] - 1]
	#feats = feats / numpy.max(feats)
	pol_feats = build_feats(feats, order=order)

	corrs = []
	for i in xrange(pol_feats.shape[1]):
		#print i, numpy.corrcoef(people, dataset[:,i])[0][1]#, numpy.cov(numpy.vstack( (people, dataset[:,i]) ) )
		corrs.append( (i, numpy.var(pol_feats[:,i])))


	for i, corr in sorted(corrs[:-1], key=lambda x: -abs(x[1]))[:50]:
		print i, corr
	
if __name__ == "__main__":
	main()
