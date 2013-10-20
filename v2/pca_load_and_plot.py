#!/usr/bin/env python

import numpy
import pickle
import matplotlib.pyplot as plt
import sys


def prepare_for_plotting(arr, threshold=1):
	avg = numpy.average(arr)
	std = numpy.std(arr)
	res = []
	for x in arr[0]:
		if abs(x - avg) > std*threshold:
			if x > avg:
				res.append(avg+std*threshold)
			else:
				res.append(avg-std*threshold)
		else:
			res.append(x)
	return res

def main():
	numpy.set_printoptions(precision=1, linewidth=284, threshold=40, edgeitems=13)
	filename2 = sys.argv[1]
	print "Loading PCA node from", filename2
	f = open(filename2,  "rb")
	pnode = pickle.load(f)
	f.close()
	print "Loading done"
	filename3 = sys.argv[2]
	print "Loading test pair from", filename3
	f = open(filename3,  "rb")
	testin, testout = pickle.load(f)
	f.close()
	print "Test in:"
	print testin
	testout = pnode.execute(testin)
	print "Testout from file:"
	print testout
	my_testout = pnode.execute(testin)
	print "Testout from here:"
	print my_testout
	print "They are equal:", testout == my_testout
	plt.figure(1)
	plt.subplot(211)
	plt.bar(range(testin.size), prepare_for_plotting(testin))
	plt.subplot(212)
	plt.bar(range(testout.size), prepare_for_plotting(testout))
	plt.show()

if __name__ == "__main__":
	main()
