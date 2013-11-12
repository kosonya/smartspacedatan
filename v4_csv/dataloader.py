#!/usr/bin/env python

import MySQLdb




class DataLoader(object):
    def __init__(self, mysql_user = "root", mysql_password = "", mysql_db = "andrew", mysql_host = "localhost", filename = "203_2013-05-14-cal.csv"):
        self.mysql_user = "root"
        self.mysql_password = ""
        self.mysql_db = "andrew"
        self.mysql_host = "localhost"
        self.filename = filename
        f = open(filename, "r")
        self.file_content = [x.split(',') for x in f.readlines()]
        f.close()
        self.processed_file = []
        for line in self.file_content:
            self.processed_file.append(self.process_one_reading(line))
        
    
    def process_one_reading(self, reading):
        res = {}
        h, m = map(int, reading[0][8:].split(':'))
        t = 3600*h + 60*m
        res["timestamp"] = t
        res["temp"] = float(reading[2])
        res["light"] = float(reading[4])
        res["pressure"] = float(reading[6])
        res["audio_p2p"] = float(reading[8])
        res["people"] = float(reading[9])
        return res
        
    
        
    def get_min_max_timestamps(self):
        _min = self.processed_file[0]["timestamp"]
        _max = self.processed_file[-1]["timestamp"]
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
    
    def load_data_bundle(self, start, stop, device_mac = "aaa", norm_coeffs = "aaa"):
        count = 0
        res = []
        for reading in self.processed_file:
            tmp = []
            timestamp = reading['timestamp']
            if start <= timestamp <= stop: 
                people = reading['people']
                for key in [x for x in reading.keys() if x not in ['timestamp', 'people']]:
                    tmp.append(reading[key])
                res.append( ([timestamp] + tmp, people) )
                count += 1
        if count < 3:
            count = 0
            res = []
        return count, res

    
def main():
    dl = DataLoader()
 #   for line in dl.processed_file:
 #       print line
    print dl.get_min_max_timestamps()
    data = dl.load_data_bundle(0, 120)
    for l in data[1]:
        print l
        
if __name__ == "__main__":
    main()