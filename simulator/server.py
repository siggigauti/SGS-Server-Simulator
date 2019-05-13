import random
from heapq import heappop
from heapq import heappush
# A general server
# Holds meta info, a scheduler, and a queue of jobs in the server (a waiting queue or an active job queue)


class Server:

    _service = None
    _scheduler = None
    _total_jobs = 0  # Total number of jobs in the system
    _total_processing_time = 0  # Total remaining processing time, also time until idle
    _server_queue = []  # A priority heap queue for jobs (should have list like: (remaining_service, job))
    _prev_arrival = 0  # The last time we had an arrival
    _qenabled = False  # Is the policy using qlearning?
    _service_rate = 0
    # Initialization, set the service rate (lambda) and the scheduler

    def __init__(self, service_rate, scheduler, *args, **kwargs):
        # self._service = service  # Can be expo, weibull, ..
        self._service_rate = service_rate
        self._scheduler = scheduler  # FIFO, PS, ..

    # For PS, keep a prio queue of sorts, of the jobs in the system running. Update upon each arrival and
    # deprture the remaining time.
    # remember: check the main schedule prio queue

    # Usage: server.get_service_time()
    # Before: nothing
    # After: returns a virtual service time, based on the server service.
    #        also updates the total processing time (virtual timepoint when the server becomes idle )
    # def get_service_time(self, job): # pragma: no cover
    #    service_time = self._service.get_service_time()
    #    if(self._total_processing_time < job._arrival_time): #If we're in 'deadspace'
    #        self._total_processing_time = job._arrival_time # We set the next idle time to be now.
    #    #Otherwise server is not idle and it will be updated after we set the enter service.
    #    return service_time

    # Usage: server.add_job(time, param)
    # Before: time is the virtual point in time of arrival. param is a list of job and world
    # After: We've scheduled the job given to depart at calculated time, calculated with arrival time.
    def add_job(self, time, param, *args, **kwargs):
        job = param[0]  # Grab the job
        world = param[1]  # Grab the world
        policy = param[2]  # Grab the policy
        # world.add_to_arr_dep() # Job gets added to the system here
        self._total_jobs += 1  # Increment number of jobs in the server
        job.set_service(job._size / self._service_rate)  # Get the service time for this job for this server from its job_size class
        enter_service = self._scheduler.enter_service(time, self._total_processing_time)
        job.set_enter_service(enter_service)
        if(self._total_processing_time < job._arrival_time):  # If we're in idle space
            self._total_processing_time = job._arrival_time + job._service_time  # Updating next idle
        else:
            self._total_processing_time += job._service_time  # otherwise we have jobs we are working on, next idle is that + new jobs service time
        world._stats.server_job_monitor_add()
        # Get a list of job instances to schedule for departure
        jobs_and_queue = self._scheduler.schedule(job, self._server_queue, self._prev_arrival)
        jobs_to_depart = jobs_and_queue[0]
        self._server_queue = jobs_and_queue[1]
        self._prev_arrival = time  # Updating prev arrival
        # Here we get the list of jobs to depart (FCFS is only 1, but e.g. PS may be many)
        for job in jobs_to_depart:
            world.schedule_event(self.departure, job._departure_time, [job, world, policy])

    # Usage: server.departure(time, param)
    # Before: time is the virtual point in time of departure, param is a list of job and world
    # After: We've decremented # of jobs in server. We report the statistic of the job to the world.
    def departure(self, time, param, *args, **kwargs):
        job = param[0]
        world = param[1]
        policy = param[2]
        # world.add_to_arr_dep() # A job has departed. Recording the event
        if self._qenabled == True:
            # How do we send signal to policy?
            policy.departure_update(self, job)  # What do I need for updating?
        # send data to job (departure)
        self._total_jobs -= 1
        world._stats.server_job_monitor_rem()
        # Send rest of data needed to job to make sure we have right stats
        world._stats.add_job(job)  # report the job to the world statistics
        # job.report_statistics(world) # Make job send the statistics of itself before leaving the system.
