#!/usr/bin/env python

import dataloader
import dataprocessor
import numpy
import math
import pickle
import random

def pdf(x, avg, std, minimum_p = 1e-20):
	if std == 0:
		if x == avg:
			return 1
		else:
			return minimum_p
	return math.exp(- ((x - avg)**2) / (2.0*(std**2))   ) / (std*math.sqrt(2*math.pi)) 

def main():
	src_file = "129A_readings.cal.csv"
	src_filename = "../../../Documents/CMU/2013-course/18697_Ole/cal.joined/" + src_file
	#random_prefix = "small_subset."
	random_prefix = ""
	#random_prefix = "decreased_zeros."
	group_by = 120*1000
	order = 1
	numpy.set_printoptions(precision=1, linewidth=210, threshold=30, edgeitems=10)

	dl = dataloader.DataLoader(filename = src_filename)
	min_t, max_t =  dl.get_min_max_timestamps()
	print min_t, max_t
	#min_t = 1377100000000
	#max_t = min_t + 1000*3600
	print min_t, max_t
	start_t = min_t
	stop_t = start_t + group_by
	
	
	matrix_dataset_raw = None
	matrix_dataset_rounded = None
	matrix_dataset_binary = None

	groupped_dataset_rounded = {}
	groupped_dataset_binary = {}

	while stop_t <= max_t:
		print "Processing from", start_t, "to", stop_t, "of from", min_t, "to", max_t, "(", 100*float(stop_t - min_t)/float(max_t - min_t), "%)"
		count, timedata_and_people = dl.load_data_bundle(start_t, stop_t)
		#print "count, timedata_and_people", count, timedata_and_people
		if count >= 3:
			print count, "rows loaded"	
			time_and_data = []
			people = []
			
			for t, p in timedata_and_people:
				#print t, p
				time_and_data.append(t)
				people.append(p)
		else:
			print "Count =", count, "skipping"
			start_t = stop_t + 1
			stop_t = start_t + group_by
			continue
		uz_data = dataprocessor.unzip_data_bundle(time_and_data)
		time_and_feats = dataprocessor.extract_all_features_from_sensors(uz_data)
		_time, pols = dataprocessor.build_polynomial_features(time_and_feats, order=order)
		pols = pols[:,1:]
		
		avg_people = numpy.mean(people)


		arr_raw_people = numpy.array(avg_people, dtype="float64").reshape( (1, 1) )
		arr_rounded_people = numpy.round(arr_raw_people)
		arr_binary_people = numpy.array(arr_rounded_people)
		if arr_binary_people[0][0] >= 0.5:
			arr_binary_people[0][0] = 1

		#if int(arr_binary_people[0][0]) == 0 and random.random() > 0.1:
		#	start_t = stop_t + 1
		#	stop_t = start_t + group_by
		#	continue
			

		raw_reading = numpy.hstack( (pols, arr_raw_people) )
		rounded_reading = numpy.hstack( (pols, arr_rounded_people) )
		binary_reading = numpy.hstack( (pols, arr_binary_people) )

		if matrix_dataset_raw == None:
			matrix_dataset_raw = raw_reading
		else:
			matrix_dataset_raw = numpy.vstack( (matrix_dataset_raw, raw_reading) )

		if matrix_dataset_rounded == None:
			matrix_dataset_rounded = rounded_reading
		else:
			matrix_dataset_rounded = numpy.vstack( (matrix_dataset_rounded, rounded_reading) )

		if matrix_dataset_binary == None:
			matrix_dataset_binary = binary_reading
		else:
			matrix_dataset_binary = numpy.vstack( (matrix_dataset_binary, binary_reading) )

		rounded_people = int(arr_rounded_people[0][0])
		binary_people = int(arr_binary_people[0][0])

		if groupped_dataset_rounded.has_key(rounded_people):
			groupped_dataset_rounded[rounded_people] = numpy.vstack( (groupped_dataset_rounded[rounded_people], pols) )
		else:
			groupped_dataset_rounded[rounded_people] = pols

		if groupped_dataset_binary.has_key(binary_people):
			groupped_dataset_binary[binary_people] = numpy.vstack( (groupped_dataset_binary[binary_people], pols) )
		else:
			groupped_dataset_binary[binary_people] = pols

		print pols
		print avg_people
		print "\n\n"
		
		start_t = stop_t + 1
		stop_t = start_t + group_by

	print matrix_dataset_raw
	fname = random_prefix + src_file + ".matrix_dataset_raw.p"
	f = open(fname, "wb")
	pickle.dump(matrix_dataset_raw, f)
	f.close()

	print matrix_dataset_rounded
	fname = random_prefix + src_file + ".matrix_dataset_rounded.p"
	f = open(fname, "wb")
	pickle.dump(matrix_dataset_rounded, f)
	f.close()

	print matrix_dataset_binary
	fname = random_prefix + src_file + ".matrix_dataset_binary.p"
	f = open(fname, "wb")
	pickle.dump(matrix_dataset_binary, f)
	f.close()

	print groupped_dataset_rounded
	fname = random_prefix + src_file + ".groupped_dataset_rounded.p"
	f = open(fname, "wb")
	pickle.dump(groupped_dataset_rounded, f)
	f.close()

	print groupped_dataset_binary
	fname = random_prefix + src_file + ".groupped_dataset_binary.p"
	f = open(fname, "wb")
	pickle.dump(groupped_dataset_binary, f)
	f.close()
	
if __name__ == "__main__":
	main()
