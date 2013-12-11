#!/usr/bin/env python

import dataloader
import dataprocessor
import numpy
import math
import pickle

def multi_pdf(x, mean, covariance):
	k = x.size
	res = 1.0 / numpy.sqrt( ( (2.0 * numpy.pi) ** k ) * numpy.linalg.det(covariance) )
	res *= numpy.exp( -0.5 * numpy.dot(numpy.dot(numpy.transpose(x - mean), numpy.linalg.pinv(covariance)), (x - mean)) )
	return res

def main():
	group_by = 120*1000
	order = 1
	#filename = "small_subset.110_readings.cal.csv.groupped_dataset_rounded.p"
	filename = "129A_readings.cal.csv.groupped_dataset_rounded.p"
	f = open(filename, "rb")
	groupped_stats = pickle.load(f)
	f.close()
	
	for key in groupped_stats.keys():
		print key, ":", groupped_stats[key].shape
		
	stats = {}
	total = sum([x.shape[0] for x in groupped_stats.values()])
	nz_total = sum([x[1].shape[0] for x in groupped_stats.items() if x[0] != 0])
	print "Total:", total
	print "Total non-zeroes:", nz_total
	for npeople in groupped_stats.keys():
		means = numpy.mean(groupped_stats[npeople], axis = 0)
		if numpy.isnan(means).any():
			continue
		covs = numpy.cov(groupped_stats[npeople].T)
		if numpy.isnan(covs).any():
			continue
		stats[npeople] = {}
		stats[npeople]["covs"] = covs
		stats[npeople]["means"] = means
		stats[npeople]["marginal"] = float(groupped_stats[npeople].shape[0])/float(total)
		print ("%d:" % npeople)
		for key in stats[npeople].keys():
			print key, ":", stats[npeople][key]
		print "\n"



	rights = 0
	nz_rights = 0

	cur_total = 0
	previous_percent_done = 0
	report_step = 0.1

	for people_true in groupped_stats.keys():
		for reading in groupped_stats[people_true]:

			pdfs = {}
			for npeople in stats.keys():
				pdfs[npeople] = multi_pdf(reading, stats[npeople]["means"], stats[npeople]["covs"]) * stats[npeople]["marginal"]
			#print pdfs
			people_estimate = max(pdfs.items(), key = lambda x: x[1])[0]
			#print pdfs
			#print people_true, people_estimate
			if people_estimate == people_true:
				rights += 1
				if people_estimate != 0:
					nz_rights += 1
			

			cur_total += 1
			percent_done = 100*float(cur_total)/total
			percent_success = 100*float(rights)/cur_total
			if percent_done - previous_percent_done >= report_step:
				print "Processing reading {} of {} ({}% done). Success rate so far: {}%".format(cur_total, total, percent_done, percent_success)
				previous_percent_done = percent_done

	

		
	print "Total:", total, "rights:", rights, "(", 100*float(rights)/float(total), "%)"
	print "Total non-zero:", nz_total, "rights:", nz_rights, "(", 100*float(nz_rights)/float(nz_total), "%)"

	
	
if __name__ == "__main__":
	main()
