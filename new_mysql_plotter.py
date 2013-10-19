#!/usr/bin/env python

import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import dataloader
import dataprocessor



class ScatterPlotter(object):
	def __init__(self, sensorx, sensory, device_id, start_date_time, end_date_time):
		self.sensorx = sensorx
		self.sensory = sensory
		self.sdt = start_date_time
		self.edt = end_date_time
		self.device_id = device_id

	def load_data(self):
		dl = dataloader.DataLoader(sensors = [self.sensorx, self.sensory], device_id = self.device_id)
		dl.load_data(start_date_time = self.sdt , end_date_time = self.edt)
		self.data = dl.raw_data()

	def process_data(self, modex, modey, group_mode, group_by):
		self.dp = dataprocessor.DataProcessor(self.data)
		self.datax, self.datay = self.dp.build_vars(var_modes = [modex, modey], group_mode = group_mode, group_by = group_by)
		self.modex = modex
		self.modey = modey
		self.group_by = group_by
		self.group_mode = group_mode
	
	def plot(self):
		plt.xlabel(self.sensorx + " (" + self.modex + ")")
		plt.ylabel(self.sensory + " (" + self.modey + ")")
		title = "Device %d\ndata from %s to %s\nreadings are grouped by %d"% (self.device_id, self.sdt, self.edt, self.group_by)
		if self.group_mode == "time":
			title += " seconds"
		plt.title(title)
		plt.plot(self.datax, self.datay, 'ro')
		plt.show()		



class HistPlotter3D(ScatterPlotter):
	def plot(self):
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		x, y = np.array(self.datax), np.array(self.datay)
		hist, xedges, yedges = np.histogram2d(x, y, bins=50)

		elements = (len(xedges) - 1) * (len(yedges) - 1)
		xpos, ypos = np.meshgrid(xedges[:-1]+0.25, yedges[:-1]+0.25)

		xpos = xpos.flatten()
		ypos = ypos.flatten()
		zpos = np.zeros(elements)
		dx = 0.5 * np.ones_like(zpos)
		dy = dx.copy()
		dz = hist.flatten()

		ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color='b', zsort='average')
		ax.set_xlabel(self.sensorx + " (" + self.modex + ")")
		ax.set_ylabel(self.sensory + " (" + self.modey + ")")
		title = "Device %d\ndata from %s to %s\nreadings are grouped by %d"% (self.device_id, self.sdt, self.edt, self.group_by)
		ax.set_zlabel("frequency")
		if self.group_mode == "time":
			title += " seconds"
		ax.set_title(title)

		plt.show()


def main():
	sp = ScatterPlotter(sensorx = "audio_p2p", sensory = "audio_p2p", device_id = 17000002, start_date_time = "2013-09-26 00:00:01", end_date_time = "2013-10-10 00:00:01")
	sp.load_data()
	sp.process_data(modex = "average absolute derivative", modey = "average", group_mode = "time", group_by = 200)
	sp.plot()

if __name__ == "__main__":
	main()

