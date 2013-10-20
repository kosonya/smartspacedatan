#!/usr/bin/env python

import datetime
import pytz
import MySQLdb
import multiprocessing


mysql_user = "root"
mysql_password = ""
mysql_db = "andrew"
mysql_host = "localhost"

parallel_threads = 6

def get_min_max_timestamps():
	global mysql_user, mysql_password, mysql_db, mysql_host
	query = "SELECT MIN(timestamp) DIV 1000, MAX(timestamp) DIV 1000 FROM readings"
	db = MySQLdb.connect(host = mysql_host, user = mysql_user, db = mysql_db, passwd = mysql_password)
	c = db.cursor()
	c.execute(query)
	_min, _max = c.fetchone()
	c.close()
	db.close()
	return _min, _max

def load_data_bundle(start, stop, device_mac):
	global mysql_user, mysql_password, mysql_db, mysql_host
	query = "SELECT timestamp DIV 1000, temp, light, humidity, pressure, audio_p2p FROM readings WHERE mac = \'%s\' AND timestamp BETWEEN %d*1000 AND %d*1000" % (device_mac, start, stop)
	db = MySQLdb.connect(host = mysql_host, user = mysql_user, db = mysql_db, passwd = mysql_password)
	c = db.cursor()
	count = c.execute(query)
	if count < 3: #completely useless
		res = None
	else:
		res = c.fetchall()
	c.close()
	db.close()
	return res

def unzip_data_bundle(data):
	return [list(x) for x in zip(*data)]


def _avg(time, data):
	return float(sum(data))/len(data)

def _max(time, data):
	return max(data)

def _variance(time, data):
	avg = _avg(data)
	res = 0
	for a in arr:
		res += (a - avg)**2
	res /= (float(len(data)))
	return res

def _derivative(time, data):
	try:
		res = []
		prevx = data[0]
		prevy = time[0]
		for i in xrange(1, len(data)):
			try:
				curx = data[i]
				cury = time[i]
				d = float(curx - prevx)/float(cury - prevy)
				res.append(d)
			except Exception as e:
				pass
			prevx = curx
			prevy = cury
		return res
	except Exception as e:
		pass
	
def _avg_derivative(time, data):
	try:
		return _avg(_derivative(time, data))
	except Exception:
		return 0

def _avg_abs_derivative(time, data):
	try:
		return _avg(map(abs, _derivative(time, data)))
	except Exception:
		return 0

def _extremums_per_second(time, data):
	try:
		prev, prevprev = data[0], data[1]
		res = 0
		for cur in data[2:]:
			if prevprev < prev > cur:
				res += 1
			elif prevprev > prev < cur:
				res += 1
			prevprev = prev
			prev = cur
		res = res / float(abs(time[-1] - time[0]))
		return res
	except:
		return 0

def extract_feature_from_sensors(time_and_data, feature):
	time, data = time_and_data[0], time_and_data[1:]
	res = [_avg([], time)]
	for sensor in data:
		if feature == "average":
			res.append(_avg(time, sensor))
		elif feature == "maximum":
			res.append(_max(time, sensor))
		elif feature == "variance":
			res.append(_var(time, sensor))
		elif feature == "average derivative":
			res.append(_avg_derivative(time, sensor))
		elif feature == "average absolute derivative":
			res.append(_avg_abs_derivative(time, sensor))
		elif feature == "extremums per second":
			res.append(_extremums_per_second(time, sensor))
	return res


def extract_feature_from_sensors_parallel_work(tsf):
	time, sensor, feature = tsf
	if feature == "average":
		return _avg(time, sensor)
	elif feature == "maximum":
		return _max(time, sensor)
	elif feature == "variance":
		return _var(time, sensor)
	elif feature == "average derivative":
		return _avg_derivative(time, sensor)
	elif feature == "average absolute derivative":
		return _avg_abs_derivative(time, sensor)
	elif feature == "extremums per second":
		return _extremums_per_second(time, sensor)

def extract_feature_from_sensors_parallel(time_and_data, feature):
	global parallel_threads
	time, data = time_and_data[0], time_and_data[1:]
	res = [_avg([], time)]
	pool = multiprocessing.Pool(parallel_threads)
	res += pool.map(extract_feature_from_sensors_parallel_work, [(time, sensor, feature) for sensor in data])
	return res


def main():
	_min, _max = get_min_max_timestamps()
	print _min, _max
	print load_data_bundle(_min, _min+10, "1703000a")
	data_bundle = load_data_bundle(_min, _min+100, "1703000a")
	uz_data_bundle = unzip_data_bundle(data_bundle)
	for arr in uz_data_bundle:
		print arr
	print ""
	for feat in extract_feature_from_sensors_parallel(uz_data_bundle, "average"):
		print feat

if __name__ == "__main__":
	main()
