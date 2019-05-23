## CPU Scheduler Simulator
This program simulates a CPU scheduler which runs processes based on a number of input metrics.
- Average arrival rate, lambda, in processes/second.  Follows Poisson Distribution.  
- Average service rate, Ts, determined by exponential distribution.
- If applicable, quantum size for Round Robin.
- Scheduling Algorithm.

List of Algorithms Used
1. First Come First Serve (FCFS)
2. Shortest Remaining Time First (SRTF)
3. Highest Response Ratio Next (HRRN)
4. Round Robin (RR)
	- Quantum 0.1
	- Quantum 0.2
Each of the above 5 algorithms are executed 30 times.  Each execution takes an increasing lambda [1, 30] processes per second.  In all there are 5 * 30 = 150 unique executions.  A script was used for efficiency and sanity.  

For each execution, the simulation ran until the 10,000th process exited the system.  After the 10,000th process arrived, the simulator continued running processes that arrived BEFORE the 10,000th arrival, and continued accepting processes that arrived AFTER the 10,000th arrival.  It wasn't until the 10,000th arrival was completed and exited the system that the simulator ended, and recorded output metrics.

## Output Metrics
For each execution, the following metrics were recorded in one of five logs, each log devoted to its respective scheduler.
- Average turnaround time
- Total throughput (processes / unit time)
- CPU utilization
- Average number of processes in ready queue.

Each of the logs was exported to a spreadsheet.  A report, included, describes the results of the metrics above.  A sample of one of the logs qq02 is included for review.

## Design 
Main Components
- CPU: fairly simple in that the main responsibility was keeping track of when the cpu was busy (running a process) or idle.  Of course, if CPU is busy, the ready queue begins to fill with process arrivals.
- Process: a single process with the following attributes:
	- Arrival time
	- CPU burst (service time)
	- Service time (for preemptive schedulers that may cut up a process' cpu time)
	- Remaining time
- Event:  discrete event.  A process may be associated with more than one event (arrival event, departure event), but an event may be associated with only one process.
	- Event type 
		- DEF: initial default 
		- ARR: arrival
		- DEP: departure
		- INT: interrupt
		- RRI: round robin interrupt
- EventQueue: where the bulk of the work occurs.  Based on the scheduling time, the event queue fills up with events, the very first being a process arrival.  If the cpu is idle, the process is serviced; the cpu turns busy, and a departure event for that process is added to the queue.  Steadily, new processes are constantly arriving, based on the given lambda.

In preemptive schedulers (SRTF and RR), a process active in the CPU can be interrupted.  In this case, the departure event is deleted from the event queue, and the respective process is pushed to the ready queue.  The ready queue is contained within the EventQueue class, though it is worth noting that they are distinct from each other.  The event queue has many complex actions taken upon it, according to the scheduler, whereas the ready queue is simply a list of processes pushed into.  Processes are plucked out, one by one, according to the scheduler.
	
## How to Run
Strongly advise to make use of runScript (automates each of the [1, 30] lambda executions).  

	python main.py <scheduler> <lambda> <serviceTime> <quantum>
	
The quantum must be included, but is ignored by all schedulers except round robin.  For example, to run scheduler 2, SRTF, with a lambda of 10 processes per second, and an average service time of 0.06:
	
	python main.py 2 10 0.06 0.01
