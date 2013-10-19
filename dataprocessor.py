import itertools
import multiprocessing


def unzip(data):
	return [map(int, x) for x in zip(*data)]

def group_by_count(data, count):
	res = []
	for i in xrange(0, len(data), count):
		res.append(data[i:i+count])
	return res

def group_by_time( time, data, dtime):
	res = []
	tmp = []
	tstart = time[0]
	for i in xrange(len(time)):
		if time[i] - tstart >= dtime:
			if tmp:
				res.append(tmp)
			tmp = []
			tstart = time[i]
		tmp.append(data[i])
	if tmp:
		res.append(tmp)
	return res

def _avg(arr):
	return float(sum(arr))/len(arr)

def _max(arr):
	return max(arr)

def _variance(arr):
	avg = _avg(arr)
	res = 0
	for a in arr:
		res += (a - avg)**2
	res /= (float(len(arr)))
	return res

def _derivative(data, time):
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
	
def _avg_derivative(data, time):
	try:
		return _avg(_derivative(data, time))
	except Exception:
		return 0

def _avg_abs_derivative(data, time):
	try:
		return _avg(map(abs, _derivative(data, time)))
	except Exception:
		return 0

def _count_extremum(arr):
	try:
		prev, prevprev = arr[0], arr[1]
		res = 0
		for cur in arr[2:]:
			if prevprev < prev > cur:
				res += 1
			elif prevprev > prev < cur:
				res += 1
			prevprev = prev
			prev = cur
		return res
	except:
		return 0


def build_vars(data, var_modes, group_mode = "time", group_by = 20, distort = False):
	print "Unzipping data (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"
	varrays = unzip(data)
	time, varrays = varrays[0], varrays[1:]
	print "Data unzipped (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"
	print "Groupping data (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"
	if group_mode == "count":
		varrays = map(lambda x: group_by_count(x, group_by), varrays)
	elif group_mode == "time":
		for i in xrange(len(varrays)):
			varrays[i] = group_by_time(time, varrays[i], group_by)
	print "Data groupped (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"

	print "Processing data (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"
	for varnum in xrange(len(varrays)):
		print "Processing array", varnum, "var_mode =", var_modes[varnum]
		if var_modes[varnum] == "average":
			varrays[varnum] = map(lambda x: _avg(x), varrays[varnum])
		elif var_modes[varnum] == "maximum":
			varrays[varnum] = map(lambda x: _max(x), varrays[varnum])
		elif var_modes[varnum] == "variance":
			varrays[varnum] = map(lambda x: _variance(x), varrays[varnum])
		elif var_modes[varnum] == "extremums":
			varrays[varnum] = map(lambda x: _count_extremum(x), varrays[varnum])
		elif var_modes[varnum] == "average derivative":
			varrays[varnum] = map(lambda x: _avg_derivative(x, time), varrays[varnum])
		elif var_modes[varnum] == "average absolute derivative":
			varrays[varnum] = map(lambda x: _avg_abs_derivative(x, time), varrays[varnum])
		print "Array", varnum, "processed", "var_mode =", var_modes[varnum]
	print "Data processed (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"


	return varrays



class DataProcessor(object):
	def __init__(self, data):
		self.data = data

	def unzip(self, data):
		return [map(int, x) for x in zip(*data)]

	def group_by_count(self, data, count):
		res = []
		for i in xrange(0, len(data), count):
			res.append(data[i:i+count])
		return res

	def group_by_time(self, time, data, dtime):
		res = []
		tmp = []
		tstart = time[0]
		for i in xrange(len(time)):
			if time[i] - tstart >= dtime:
				if tmp:
					res.append(tmp)
				tmp = []
				tstart = time[i]
			tmp.append(data[i])
		if tmp:
			res.append(tmp)
		return res

	def _avg(self, arr):
		return float(sum(arr))/len(arr)

	def _max(self, arr):
		return max(arr)

	def _variance(self, arr):
		avg = self._avg(arr)
		res = 0
		for a in arr:
			res += (a - avg)**2
		res /= (float(len(arr)))
		return res

	def _derivative(self, data, time):
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
	
	def _avg_derivative(self, data, time):
		try:
			return self._avg(self._derivative(data, time))
		except Exception:
			return 0

	def _avg_abs_derivative(self, data, time):
		try:
			return self._avg(map(abs, self._derivative(data, time)))
		except Exception:
			return 0

	def _count_extremum(self, arr):
		try:
			prev, prevprev = arr[0], arr[1]
			res = 0
			for cur in arr[2:]:
				if prevprev < prev > cur:
					res += 1
				elif prevprev > prev < cur:
					res += 1
				prevprev = prev
				prev = cur
			return res
		except:
			return 0

	def build_vars(self, var_modes, group_mode = "time", group_by = 20, distort = False):
		print "Unzipping data (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"
		varrays = self.unzip(self.data)
		time, varrays = varrays[0], varrays[1:]
		print "Data unzipped (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"
		print "Groupping data (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"
		if group_mode == "count":
			varrays = map(lambda x: self.group_by_count(x, group_by), varrays)
		elif group_mode == "time":
			for i in xrange(len(varrays)):
				varrays[i] = self.group_by_time(time, varrays[i], group_by)
		print "Data groupped (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"

		print "Processing data (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"
		for varnum in xrange(len(varrays)):
			print "Processing array", varnum, "var_mode =", var_modes[varnum]
			if var_modes[varnum] == "average":
				varrays[varnum] = map(lambda x: self._avg(x), varrays[varnum])
			elif var_modes[varnum] == "maximum":
				varrays[varnum] = map(lambda x: self._max(x), varrays[varnum])
			elif var_modes[varnum] == "variance":
				varrays[varnum] = map(lambda x: self._variance(x), varrays[varnum])
			elif var_modes[varnum] == "extremums":
				varrays[varnum] = map(lambda x: self._count_extremum(x), varrays[varnum])
			elif var_modes[varnum] == "average derivative":
				varrays[varnum] = map(lambda x: self._avg_derivative(x, time), varrays[varnum])
			elif var_modes[varnum] == "average absolute derivative":
				varrays[varnum] = map(lambda x: self._avg_abs_derivative(x, time), varrays[varnum])
			print "Array", varnum, "processed", "var_mode =", var_modes[varnum]
		print "Data processed (var_modes =", var_modes, "group_mode = ", group_mode, "group_by =", group_by, "distort =", distort, ")"
		print "Now we have", len(varrays[0]), "data points"

		if distort:
			for i in xrange(len(varrays)):
				self.anomaly_filter(varrays[i])
	
		return varrays

	def anomaly_filter(self, data, sigma_threshold = 100):
		avg = self._avg(data)
		var = self._variance(data)
		for i in xrange(len(data)-1, -1, -1):
			if abs(avg - data[i]) > var*sigma_threshold:
				if data[i] > avg:
					data[i] = avg + var*sigma_threshold
				else:
					data[i] = avg - var*sigma_threshold

	def extract_all_features(self, all_var_modes = ["average", "maximum", "variance", "extremums", "average derivative", "average absolute derivative"], group_mode = "time", group_by = 20, distort = False):
		print "Extracting all features"
		all_varrays = []
		for var_mode in all_var_modes:
			print "Extracting feature:", var_mode
			all_varrays += self.build_vars([var_mode for _ in xrange(len(self.data[0])-1)], group_mode, group_by, distort)
			print "Feature extracted:", var_mode
		print "All features extracted. Total:", len(all_varrays)
		return all_varrays

