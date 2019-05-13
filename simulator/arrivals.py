from simulator.job import Job
import numpy


class PoissonArrival():
    _rate = 1
    _random_generator = None
    _job_size_generator = None
    _from_file = False
    _file_data = None
    _last_job = None

    # has a poisson rate of arrival as attribute, defaults to 1
    def __init__(self, rate, job_sizes, arr_seed=None, file=None, *args, **kwargs):
        if arr_seed is not None:
            self._random_generator = numpy.random.RandomState(arr_seed)
        else:
            self._random_generator = numpy.random.RandomState()  # Use default seed for generator
        self._job_size_generator = job_sizes
        self._job_size_generator.set_random_stream(self._random_generator)
        self._rate = rate  # Setting the arrival rate
        if file:
            self._from_file = True
            self._file_data = file  # List of tuples (arr, size)

    # Generate a single poisson arrival
    def generate_arrival(self, time, param):
        dispatcher = param[0]  # Get the associated dispatcher
        world = param[1]  # Get the global
        job_nr = world._stats.number_of_jobs
        next_time = self._random_generator.exponential(1 / self._rate)
        if self._from_file is False:
            self._last_job = Job(time, self._job_size_generator.get_service_time())  # Takes given arrival time and creates a job with given size distribution
        else:
            try:
                self._last_job = Job(self._file_data[job_nr][0], self._file_data[job_nr][1])
            except IndexError as e:
                self._last_job = None  # If this executes, we are generating jobs that will never finish before simtime runs out.
        if self._last_job is not None:
            next_event = time + next_time  # Time of next arrival

            dispatcher.make_decision([self._last_job, world])  # Send the job to the dispatcher for a decision

            # Will set a new arrival event, with given time and list of this dispatcher and the world.

            world.schedule_event(self.generate_arrival, next_event, [dispatcher, world])
            world._stats.increment_jobs()  # increment the number of jobs that have passed through system

    # Create first arrival
    def first_arrival(self, param):
        dispatcher = param[0]  # Get the associated dispatcher
        world = param[1]  # Get the global instance
        first_event = self._random_generator.exponential(1 / self._rate)

        # Will set a new arrival event, with given time and list of this dispatcher and the world.
        world.schedule_event(self.generate_arrival, first_event, [dispatcher, world])
