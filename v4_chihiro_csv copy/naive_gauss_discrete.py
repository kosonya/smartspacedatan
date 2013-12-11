#!/usr/bin/env python

import dataloader
import dataprocessor
import numpy
import math
import pickle

def pdf(x, avg, std, minimum_p = 1e-20):
	if std == 0:
		if x == avg:
			return 1
		else:
			return minimum_p
	return math.exp(- ((x - avg)**2) / (2.0*(std**2))   ) / (std*math.sqrt(2*math.pi)) 

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
		stats[npeople] = {}
		stats[npeople]["avgs"] = numpy.mean(groupped_stats[npeople], axis = 0)
		stats[npeople]["stds"] = numpy.std(groupped_stats[npeople], axis = 0)
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
				cur_pdf = 1
				for i in xrange(reading.size):
					cur_pdf *= pdf(reading[i], stats[npeople]["avgs"][i], stats[npeople]["stds"][i])
				cur_pdf *= stats[npeople]["marginal"]
				pdfs[npeople] = cur_pdf
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
