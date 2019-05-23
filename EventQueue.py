import random
import math
import copy 
import operator
import os
from EventQueue import *
from Cpu import *
from Process import *
from Event import *

class EventQueue:

	def __init__(self, dac, sch, aar, ast, quantum):
		
		self.scheduler = int(sch)
		self.evList = []
		self.rdList = []
		self.defaultArrivalCount = int(dac)
		self.averageArrivalRate = int(aar)	# lambda
		self.averageServiceTime = float(ast)	# Ts
		self.quantum = float(quantum)	
		self.lastQuantStart = float(0.0)
		self.averageServiceRate = float(1/self.averageServiceTime)
		self.handledProcessCount = int(0)
		self.newProcessID = int(0)
		self.latestArrivalTime = float(0.0)
		self.nextDepartureTime = float(0.0)
		self.cpu = Cpu()
		self.systemClock = float(0.0)

		# Metrics
		self.rho = float(0.0)
		self.totalTurnaroundTime = float(0.0)
		self.totalWaitTime = float(0.0)
		self.averageTurnaroundTime = float()	# Tq = sum(tats) / procCount
		self.averageWaitTime = float()			# Tw = sum(wts) / procCount
		self.averageRQcount	= float()			# w = lambda * Tw
		self.throughput = float()				# t = totalProc / totalTime
		self.totalArrivals = int(0)				# handledProc + readyQueueLen
		self.computedLambda = float(0.0)		# actual average arrival rate

		# Log File
		self.fileName = str()
		if (self.scheduler == 1):
			self.fileName = "fcfsData.txt"
		elif (self.scheduler == 2):
			self.fileName = "srtfData.txt"
		elif (self.scheduler == 3):
			self.fileName = "hrrnData.txt"
		elif (self.scheduler == 4):
			self.fileName = "rr" + str((self.quantum))[2:] + ".txt"
		
		self.f = open(self.fileName, "a+")

		with open(self.fileName) as self.f:
			self.data = self.f.readlines()

		# print "\noldData:"
		# print self.data

		if (len(self.data) == 0):
			#print "file empty!!!"
			self.data.append("lambda,\n")
			self.data.append("Tq,\n")
			self.data.append("thr,\n")
			self.data.append("rho,\n")
			self.data.append("w,\n")

		# print "\ngenData"
		# print self.data

		self.f.close()


	def printEventQueue(self):
		#self.evList.sort(key=lambda x: x.time, reverse=False)
		if not self.evList:
			print "  [ ]"
		else:
			for ev in self.evList:
				ev.printEvent()	

	def printReadyQueue(self):
		#self.rdList.sort(key=lambda x: x.time, reverse=False)
		if not self.rdList:
			print "  [ ]"
		else:
			for ev in self.rdList:
				ev.printEvent()			

	def genBurst(self):
		newBurst = float(0.0)
		while (newBurst <= 0.0):
			# print "\tnewBurst:", newBurst
			realRand = random.random()
			# print "\trealRand:", realRand
			newBurst = float( (-math.log(1 - realRand) / self.averageServiceRate) )
			# print "\tnewBurst:", newBurst
		return newBurst

	def genExpo(self):
		newExpo = float(0.0)
		while (newExpo <= 0.0):
			realRand = random.random()
			newExpo = float( (-math.log(1 - realRand) / self.averageArrivalRate) )
		return newExpo

	def genArrivalEvent(self):

		burst = self.genBurst()
		arrDiff = self.genExpo()
		self.latestArrivalTime += arrDiff
		self.newProcessID += 1
		self.evList.append(Event())

		self.evList[-1].evType = "ARR"
		self.evList[-1].time = self.latestArrivalTime
		self.evList[-1].proc.id = self.newProcessID
		self.evList[-1].proc.aTime = self.latestArrivalTime
		self.evList[-1].proc.burst = burst
		self.evList[-1].proc.sTime = 0.0
		self.evList[-1].proc.rTime = burst

		# TESTPRINT
		#print "\nCreated new arrival event."
		#print "Current event queue:"
		self.evList.sort(key=lambda x: x.time)	# Good!  Evlist must be in order no exceptions.
		#self.printEventQueue()		

	def genDepartEvent(self, arrEv):
		
		self.evList.append(Event())

		self.evList[-1].evType = "DEP"
		self.evList[-1].proc = copy.deepcopy(arrEv.proc)
		self.evList[-1].time = self.systemClock + self.evList[-1].proc.rTime
		self.nextDepartureTime = self.evList[-1].time

		# TESTPRINT
		#print "\nCreated new departure event."
		#print "Current event queue:"
		self.evList.sort(key=lambda x: x.time)	# Good!  Evlist must be in order no exceptions.
		#self.printEventQueue()	

	def scheduleRR(self, ev):
		#print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ scheduleRR()..."
		self.genDepartEvent(ev)		# Generate default departure event (i.e. load to cpu)
		self.lastQuantStart = self.systemClock 	# Update most recent quantum start time.
		#print "\nlastQuantStart:", format(self.lastQuantStart, '.4f')
		
		if (ev.proc.rTime > self.quantum): 			# If the new event's rTime is greater than quantum, schedule an interrupt.
			self.evList.append(Event())		
			self.evList[-1].evType = "RRI"
			self.evList[-1].time = self.systemClock + self.quantum 
			self.evList.sort(key=lambda x: x.time)
			#print "Added RRI event."
			#self.printEventQueue()


	def chooseFromRQ(self):

		if (self.scheduler == 1):	# FCFS
			#print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"		
			#print "\nBefore sort:"
			#self.printReadyQueue()
			#print "\nAfter sort:"
			self.rdList.sort(key=lambda x: x.time)
			#self.printReadyQueue()
			# Put oldest event first.
			self.genDepartEvent(self.rdList.pop(0))

		elif (self.scheduler == 2):	# SRTF
			#print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
			# Grab lowest rTime
			self.rdList.sort(key=lambda x: x.proc.rTime)
			self.genDepartEvent(self.rdList.pop(0))

		elif (self.scheduler == 3):	# HRRN
			#print "\n****************************"
			# Grab stats of first event in ready list.
			wait = self.systemClock - self.rdList[0].proc.aTime 	# wait = currentTime - arrivalTime
			ratio = (wait + self.rdList[0].proc.burst) / self.rdList[0].proc.burst 	# ratio = (wait + processBurst) / processBurst
			index = 0
			#print "\nRatio of first event:", format(ratio, '.4f')
			for x, ev in enumerate(self.rdList):
				wait = self.systemClock - self.rdList[x].proc.aTime 
				newRatio =(wait + self.rdList[x].proc.burst) / self.rdList[x].proc.burst  	
				#print "\nRatio of event:", x, ":", format(newRatio, '.4f')
				if newRatio > ratio:
					ratio = newRatio
					index = x
			#print "\nChose event:"
			#self.rdList[index].printEvent()
			self.genDepartEvent(self.rdList.pop(index))

		elif (self.scheduler == 4):	# RR
			#print "\nChoosing from ready list..."
			# Simply pop oldest item off ready queue and schedule as normal.
			self.scheduleRR(self.rdList.pop(0))

		else:
			print "ERROR! Unknown scheduler type detected."
			sys.exit(0)

	def handleNextEvent(self):

		if (not self.evList):
			print "ERROR! handleNextEvent met empty event list\n"
			sys.exit(0)
		# This section not schedule-dependent; always pop NEXT event in time, never jump ahead.
		nextEv = self.evList.pop(0)
		self.systemClock = nextEv.time
		#print "\nSYSTEM_CLOCK:", format(self.systemClock, '.4f')
		#print "cpuActive:", self.cpu.isActive()
		#print "Handling next event."

		if (nextEv.evType == "ARR"):
			#print "Arrival event next."

			#If cpu is idle and ready queue empty, ALL schedulers automatically load to cpu.
			if ((self.cpu.isActive() == False) and not self.rdList):

				if (self.scheduler != 4):
					#print "Cpu idle & ready list empty."
					self.genDepartEvent(copy.deepcopy(nextEv))
					self.cpu.setActive(self.systemClock)
				else:
					#print "Cpu idle & ready list empty."
					self.scheduleRR(nextEv)
					self.cpu.setActive(self.systemClock)
	
			# Otherwise, we must determine if scheduler is preemptive or not.
			else:
				# If nonpreemptive, simply push new arrival to ready list.
				if (self.scheduler == 1 or self.scheduler == 3):
					#print "Pushing new event to ready list."
					self.rdList.append(nextEv)	
					#self.rdList.sort(key=lambda x: x.time, reverse=False)  # Only change when choosing new event.
			
				elif (self.scheduler == 2):			
					#print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"					
					# Grab departure event index. (The process logically inside cpu.)
					index = int()
					for x, ev in enumerate(self.evList):
						if ev.evType == "DEP":
							index = x
							break
					#print "\nindex:", index
					# Update cpu-process metrics.
					#print "\nBefore update:"
					#self.evList[index].printEvent()
					# remTime = depTime - systemTime
					self.evList[index].proc.rTime = self.evList[index].time - self.systemClock
					# servTime = burst - remTime
					self.evList[index].proc.sTime = self.evList[index].proc.burst - self.evList[index].proc.rTime 
					#print "\nAfter udpate:"
					#self.evList[index].printEvent()

					if (self.evList[index].proc.rTime > nextEv.proc.burst):
						# New event interrupts old event.
						self.evList[index].evType = "INT"
						self.evList[index].time = self.systemClock
						self.rdList.append(self.evList.pop(index))
						#print "\nOld event pushed to ready queue:"
						#self.printReadyQueue()
						self.genDepartEvent(nextEv)
					else:
						# New event goes to ready list.
						#print "\nNew event pushed to ready list"
						self.rdList.append(nextEv)
						#self.printReadyQueue()

				elif (self.scheduler == 4):
					
					if ((self.cpu.isActive() == True) and (not self.rdList)):	# If cpu active and rdList empty...
						#print "Cpu active & rdList empty."
						# Test if active process quantum is met.
						quantDur = float(self.systemClock - self.lastQuantStart)
						#print "quantDur:", format(quantDur, '.2f')
						# If recent quantum duration is greater than quantum, interrupt active process.
						if (quantDur > self.quantum):
							#print "Quantum exceeded.  Interrupting old process.  Scheduling new process."
							# Grab active process location in evList.
							index = int()
							for x, ev in enumerate(self.evList):
								if ev.evType == "DEP":
									index = x
									break
							# Old process remaining time = original departure time - current time.
							self.evList[index].proc.rTime = self.evList[index].time - self.systemClock
							# Old process served time = burst - remaining time
							self.evList[index].proc.sTime = self.evList[index].proc.burst - self.evList[index].proc.rTime
							self.evList[index].evType = "INT"
							self.evList[index].time = self.systemClock # Bookkeeping: record time of interruption.
							self.rdList.append(self.evList.pop(index))	# Push old event to END of ready list.  No sorting!
							#print "Ready queue:"
							#self.printReadyQueue()
							# Finally, schedule new process.
							self.scheduleRR(nextEv)
						# If quantum not met, new event gets appended to end of ready list.
						else:
							#print "quantDur < quantum.  Appending new arrival to end of ready list."
							self.rdList.append(nextEv)

					# If cpu active and rdList full.
					elif (self.cpu.isActive() == True and self.rdList):	
						#print "Cpu active and ready list not empty.  Appending new event to end of ready list."
						self.rdList.append(nextEv)
						#self.printReadyQueue()

				else:
					print "ERROR! Unknown scheduler type detected."
					sys.exit(0)

		elif (nextEv.evType == "DEP"):

			# Grab metrics.
			#print "Departure event next."
			self.handledProcessCount += 1
			tat = float(self.systemClock - nextEv.proc.aTime)	# turnaround time
			#print "TAT:", tat
			#print "Burst:", nextEv.proc.burst			
			#print "wt:", (self.systemClock - nextEv.proc.aTime - nextEv.proc.burst)
			wt = float(tat - nextEv.proc.burst)	# wait time
			if (abs(wt) <= 0.0001):		# ghetto fix
				wt = 0
			#print "WT:", wt
			self.totalTurnaroundTime += tat
			#print "TotalTAT:", self.totalTurnaroundTime
			self.totalWaitTime += wt
			#print "TotalWT:", self.totalWaitTime

			if (self.rdList):	# If ready list NOT empty, pop next ready ev and load to cpu.
				#print "Ready list not empty.  Loading next event to cpu."
				self.chooseFromRQ()
		
			else:	# If ready list is empty, update cpuIdle.
				self.cpu.setIdle(self.systemClock)
				#print "Ready list empty.  cpuActive:", self.cpu.isActive()
				#print "cpuActiveTotal:", self.cpu.activeTotal
		
		elif (nextEv.evType == "INT"):
			pass
		elif (nextEv.evType == "RRI"):
			#print "RRI event next."

			if (self.rdList):
				#print "Ready list not empty.  Interrupting loaded event.  Sheduling next item in ready queue."
				# Grab active process location in evList.
				index = int()
				for x, ev in enumerate(self.evList):
					if ev.evType == "DEP":
						index = x
						break
				# Old process remaining time = original departure time - current time.
				self.evList[index].proc.rTime = self.evList[index].time - self.systemClock
				# Old process served time = burst - remaining time
				self.evList[index].proc.sTime = self.evList[index].proc.burst - self.evList[index].proc.rTime
				self.evList[index].evType = "INT"
				self.evList[index].time = self.systemClock # Bookkeeping: record time of interruption.	
				# Push interrupted event to END of ready list.
				self.rdList.append(self.evList.pop(index))
				#print "Ready Queue:"
				#self.printReadyQueue()
				# Schedule next event in ready list.
				self.scheduleRR(self.rdList.pop(0))
			# If the ready list is empty, allow active process to continue unimpeded until next arrival.
			else:				
				#print "Ready list empty.  Interrupt ignored."
				pass
				# RRI event will automatically be deleted at end of function.

		else:
			print "ERROR: unknown data type in event list!"

		del nextEv		

	def run(self):

		while (self.handledProcessCount < self.defaultArrivalCount):
			#print "\n********** HANDLED PROCESS COUNT:", self.handledProcessCount
			#print "Current event queue:"
			#self.printEventQueue()
			#print "Current ready queue:"
			#self.printReadyQueue()

			if not (self.evList):
				#print "\nevList empty.  Generating new arrival event."
				self.genArrivalEvent()
			
			self.handleNextEvent()

			while (self.latestArrivalTime < self.nextDepartureTime):
				#print "latestArrivalTime:", format(self.latestArrivalTime, '.4f'), "  nextDepartureTime:", format(self.nextDepartureTime, '.4f') 
				self.genArrivalEvent()


		# Check final metrics
		#print "\nGetting final metrics..."
		if (self.cpu.isActive() == True): # If cpu active at last moment, must cancel to get final cpu metrics.
			self.cpu.setIdle(self.systemClock)	
		self.averageTurnaroundTime = self.totalTurnaroundTime / self.handledProcessCount
		self.averageWaitTime = self.totalWaitTime / self.handledProcessCount
		self.averageRQcount	= self.averageArrivalRate * self.averageWaitTime
		self.throughput = self.handledProcessCount / self.systemClock
		self.rho = self.cpu.activeTotal / self.systemClock
		self.totalArrivals = self.handledProcessCount + len(self.rdList)
		self.computedLambda = self.totalArrivals / self.systemClock

		# Write results to text file.
		# print "\nnewdata"
		# print self.data
		
		self.f = open(self.fileName, "w")

		self.data[0] = self.data[0].replace("\n", "")
		self.data[0] += str(self.averageArrivalRate)
		self.data[0] += ",\n"
		#print self.data[0]
		self.f.write (self.data[0])

		self.data[1] = self.data[1].replace("\n", "")
		self.data[1] += str(self.averageTurnaroundTime)
		self.data[1] += ",\n"
		#print self.data[1]		
		self.f.write (self.data[1])

		self.data[2] = self.data[2].replace("\n", "")
		self.data[2] += str(self.throughput)
		self.data[2] += ",\n"
		#print self.data[2]		
		self.f.write (self.data[2])

		self.data[3] = self.data[3].replace("\n", "")
		self.data[3] += str(self.rho)
		self.data[3] += ",\n"
		#print self.data[3]		
		self.f.write (self.data[3])

		self.data[4] = self.data[4].replace("\n", "")
		self.data[4] += str(self.averageRQcount)
		self.data[4] += ",\n"
		#print self.data[4]		
		self.f.write (self.data[4])

		self.f.close()


