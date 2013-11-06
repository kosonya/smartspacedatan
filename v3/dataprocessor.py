#!/usr/bin/env python

import multiprocessing
import itertools
import numpy

parallel_threads = 6
dtype = "float64"

def unzip_data_bundle(data):
    return [list(x) for x in zip(*data)]


def _avg(_time, data):
    return float(sum(data))/len(data)

def _max(_time, data):
    return max(data)

def _variance(_time, data):
    avg = _avg(_time, data)
    res = 0
    for a in data:
        res += (a - avg)**2
    res /= (float(len(data)))
    return res

def _derivative(_time, data):
    try:
        res = []
        prevx = data[0]
        prevy = _time[0]
        for i in xrange(1, len(data)):
            try:
                curx = data[i]
                cury = _time[i]
                d = float(curx - prevx)/float(cury - prevy)
                res.append(d)
            except Exception as e:
                pass
            prevx = curx
            prevy = cury
        return res
    except Exception as e:
        print e
        return 0
    
def _avg_derivative(_time, data):
    try:
        res = _avg([], _derivative(_time, data))
        return res
    except Exception as e:
        print e
        return 0

def _avg_abs_derivative(_time, data):
    try:
        return _avg([], map(abs, _derivative(_time, data)))
    except Exception as e:
        print e
        return 0

def _extremums_per_second(_time, data):
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
        res = res / float(abs(_time[-1] - _time[0]))
        return res
    except:
        return 0

def extract_feature_from_sensors(time_and_data, feature):
    _time, data = time_and_data[0], time_and_data[1:]
    res = [_avg([], _time)]
    for sensor in data:
        if feature == "average":
            res.append(_avg(_time, sensor))
        elif feature == "maximum":
            res.append(_max(_time, sensor))
        elif feature == "variance":
            res.append(_variance(_time, sensor))
        elif feature == "average derivative":
            res.append(_avg_derivative(_time, sensor))
        elif feature == "average absolute derivative":
            res.append(_avg_abs_derivative(_time, sensor))
        elif feature == "extremums per second":
            res.append(_extremums_per_second(_time, sensor))
    return res


def extract_feature_from_sensors_parallel_work(tsf):
    _time, sensor, feature = tsf
    if feature == "average":
        return _avg(_time, sensor)
    elif feature == "maximum":
        return _max(_time, sensor)
    elif feature == "variance":
        return _variance(_time, sensor)
    elif feature == "average derivative":
        return _avg_derivative(_time, sensor)
    elif feature == "average absolute derivative":
        return _avg_abs_derivative(_time, sensor)
    elif feature == "extremums per second":
        return _extremums_per_second(_time, sensor)

def extract_feature_from_sensors_parallel(time_and_data, feature):
    global parallel_threads
    _time, data = time_and_data[0], time_and_data[1:]
    res = [_avg([], _time)]
    pool = multiprocessing.Pool(parallel_threads)
    res += pool.map(extract_feature_from_sensors_parallel_work, [(_time, sensor, feature) for sensor in data])
    return res


def extract_all_features_from_sensors(time_and_data, features = ["average", "maximum", "variance", "average derivative", "average absolute derivative", "extremums per second"]):
    _time=time_and_data[0]
    res = [_avg([], _time)]
    for feature in features:
        feats = extract_feature_from_sensors(time_and_data, feature)[1:]
        res += feats
    return res

def build_polynomial_features(time_and_feats, order=3):
    global dtype
    _time, data = time_and_feats[0], [1] + time_and_feats[1:]
    res = []
    for terms in itertools.combinations_with_replacement(data, order):
        res.append(reduce(lambda x, y: x * y, terms, 1))
    return _time, numpy.array(res, dtype = dtype).reshape(1, len(res))


def build_polynomial_features_parallel_work(terms):
    return reduce(lambda x, y: x*y, terms, 1)



def build_polynomial_features_parallel(time_and_feats, order=3):
    global dtype, parallel_threads
    _time, data = time_and_feats[0], [1] + time_and_feats[1:]
    pool = multiprocessing.Pool(parallel_threads)
    res = pool.map(build_polynomial_features_parallel_work, itertools.combinations_with_replacement(data, order))

    return _time, numpy.array(res, dtype = dtype).reshape(1, len(res))
