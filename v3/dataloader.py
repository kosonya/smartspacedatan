#!/usr/bin/env python

import MySQLdb




class DataLoader(object):
    def __init__(self, mysql_user = "root", mysql_password = "", mysql_db = "andrew", mysql_host = "localhost"):
        self.mysql_user = "root"
        self.mysql_password = ""
        self.mysql_db = "andrew"
        self.mysql_host = "localhost"
        
    def get_min_max_timestamps(self):
        query = "SELECT MIN(timestamp) DIV 1000, MAX(timestamp) DIV 1000 FROM readings"
        db = MySQLdb.connect(host = self.mysql_host, user = self.mysql_user, db = self.mysql_db, passwd = self.mysql_password)
        c = db.cursor()
        c.execute(query)
        _min, _max = c.fetchone()
        c.close()
        db.close()
        return _min, _max
    
    def fetch_all_macs(self):
        query = "SELECT mac FROM sensors"
        db = MySQLdb.connect(host = self.mysql_host, user = self.mysql_user, db = self.mysql_db, passwd = self.mysql_password)
        c = db.cursor()
        c.execute(query)
        res = [x[0] for x in c.fetchall()]
        c.close()
        db.close()
        return res
    
    def load_data_bundle(self, start, stop, device_mac):
        query = "SELECT timestamp DIV 1000, temp, light, humidity, pressure, audio_p2p, motion FROM readings WHERE mac = \'%s\' AND timestamp BETWEEN %d*1000 AND %d*1000" % (device_mac, start, stop)
        db = MySQLdb.connect(host = self.mysql_host, user = self.mysql_user, db = self.mysql_db, passwd = self.mysql_password)
        c = db.cursor()
        count = c.execute(query)
        if count < 3: #completely useless
            res = None
            count = 0
        else:
            res = c.fetchall()
        c.close()
        db.close()
        return count, res
