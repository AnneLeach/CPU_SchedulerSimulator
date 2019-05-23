from Process import *

class Event:

	def __init__(self):
		self.evType = "DEF"
		self.time = float(0)
		self.proc = Process()

	def printEvent(self):
		print "  [ TYPE: " + str(self.evType) + ", TIME: " + format(self.time, '.4f') + ", PID: " \
			+ str(self.proc.id) + ", BURST: " + format(self.proc.burst, '.4f') +  ", A_TIME: " \
			+ format(self.proc.aTime, '.4f') + ", S_TIME: " + format(self.proc.sTime, '.4f') + ", R_TIME: " \
			+ format(self.proc.rTime, '.4f') + " ]"		

			