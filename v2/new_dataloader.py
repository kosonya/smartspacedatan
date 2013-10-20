#!/usr/bin/env python

import MySQLdb

mysql_user = "root"
mysql_password = ""
mysql_db = "andrew"
mysql_host = "localhost"


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

def fetch_all_macs():
	global mysql_user, mysql_password, mysql_db, mysql_host
	query = "SELECT mac FROM sensors"
	db = MySQLdb.connect(host = mysql_host, user = mysql_user, db = mysql_db, passwd = mysql_password)
	c = db.cursor()
	c.execute(query)
	res = [x[0] for x in c.fetchall()]
	c.close()
	db.close()
	return res

def load_data_bundle(start, stop, device_mac):
	global mysql_user, mysql_password, mysql_db, mysql_host
	query = "SELECT timestamp DIV 1000, temp, light, humidity, pressure, audio_p2p, motion FROM readings WHERE mac = \'%s\' AND timestamp BETWEEN %d*1000 AND %d*1000" % (device_mac, start, stop)
	db = MySQLdb.connect(host = mysql_host, user = mysql_user, db = mysql_db, passwd = mysql_password)
	c = db.cursor()
	count = c.execute(query)
	if count < 3: #completely useless
		res = None
	else:
		res = c.fetchall()
	c.close()
	db.close()
	return count, res
