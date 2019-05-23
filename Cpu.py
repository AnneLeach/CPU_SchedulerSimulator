#from Process import *
import sys

class Cpu:

	def __init__(self):

		self.cpuActive = bool(False)
		self.activeStart = float(0.0)
		self.activeTotal = float(0.0)
		#self.activeProcess = Process()
		
	def setActive(self, sysClock):
		if self.cpuActive == True:
			print "ERROR!  Attempt to activate active cpu."
			sys.exit(0)
		else:
			self.activeStart = sysClock
			self.cpuActive = True

	def setIdle(self, sysClock):
		if self.cpuActive == False:
			print "ERROR!  Attempt to idle idle cpu."
			sys.exit(0)
		else:
			activeTime = float(sysClock - self.activeStart)
			self.activeTotal += activeTime
			self.cpuActive = False

	def isActive(self):
		return self.cpuActive