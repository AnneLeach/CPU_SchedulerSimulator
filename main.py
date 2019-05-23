import sys
from EventQueue import *
from Cpu import *
from Process import *
from Event import *

defArrCount = 10000
divider = "\n----------------------------------------------------------------------------------------------------------------"
print divider
print "Welcome to the Simulator"

# Test user input.
#print "Number of command line arguments:", len(sys.argv);
#print "List of command line arguments: ", str(sys.argv);

if ((len(sys.argv) < 5)) or not (0 < int(sys.argv[1]) < 5):
	print "\nERROR: invalid commandline input " \
	"\nCommand line:   <scheduler>   <lambda>   <Ts>   <quantum>" \
	"\nScheduler: [1, FCFS], [2, SRTF], [3, HRRN], [4, RR]" \
	"\nExample: ./main 2 15 0.06 0.01"
	print divider
	sys.exit(0)


eq = EventQueue(defArrCount, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]);
eq.run()

print
print "Scheduler:", eq.scheduler
print "Tq:", eq.averageTurnaroundTime
print "Tw:", eq.averageWaitTime
print "w:", eq.averageRQcount
print "th:", eq.throughput
print "system time:", eq.systemClock
print "cpu busy time:", eq.cpu.activeTotal
print "rho:", format(eq.rho, '.2f')
print "totalArrivals:", eq.totalArrivals
print "given lambda:", sys.argv[2]
print "computed lambda:", eq.computedLambda

# print divider, "\n"