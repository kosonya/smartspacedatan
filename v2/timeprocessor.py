#!/usr/bin/env python

import datetime
import pytz
import calendar

time_format = "%Y-%m-%d %H:%M:%S"
our_timezone = "US/Pacific"



def from_unixtime(timestamp):
	global time_format
	return datetime.datetime.fromtimestamp(timestamp).strftime(time_format)

def to_unixtime(time_date): #dirty workaround - timestamps are not in utc
	global time_format, out_timezone
	dt = datetime.datetime.strptime(time_date, time_format)
	tz = pytz.timezone(our_timezone)
	dt1 = tz.localize(dt)
	res = calendar.timegm(dt1.utctimetuple())
	return res
