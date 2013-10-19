import MySQLdb

class DataLoader(object):
	def __init__(self, sensors, device_id, db_host = "localhost", db_user = "root", db_password = "", db_database = "andrew"):
		self.db_host = db_host
		self.db_user = db_user
		self.db_password = db_password
		self.db_database = db_database
		self.sensors = sensors
		self.device_id = device_id

	def load_data(self, start_date_time, end_date_time, our_timezone = "+07:00"):
		to_timestamp = lambda x: "1000*UNIX_TIMESTAMP(CONVERT_TZ(\'%s\', \'%s\', \'+00:00\'))" % (str(x), str(our_timezone))
		query = "SELECT timestamp DIV 1000, "
		query += ", ".join(self.sensors)
		query += " FROM readings"
		query += " WHERE"
		query += " mac = \'%d\'" % self.device_id
		query += " AND timestamp BETWEEN " + to_timestamp(start_date_time) + " AND " + to_timestamp(end_date_time)
		print query
		print "Loading data"
		db = MySQLdb.connect(host=self.db_host, user=self.db_user, passwd=self.db_password, db=self.db_database)
		c = db.cursor()

		c.execute(query)

		self.data = c.fetchall()
		c.close()
		db.close()
		print "Data loaded"

	def raw_data(self):
		return self.data
