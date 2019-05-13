# A general Job instance
# Holds information about itself, such as arrival time, service time,
# remaining service time and much more.


class Job():
    _arrival_time = 0
    _enter_service = 0
    _departure_time = 0
    _service_time = 0
    _remaining_service = 0
    _sojourn_time = 0
    _work_done = 0
    _waiting_time = 0
    _size = 0

    # Initialization, takes in a (virtual) arrival time
    def __init__(self, arrival, size, *args, **kwargs):
        self._arrival_time = arrival
        self._size = size

    # Used for comparisons in the heap queue
    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return True
        return False

    # Usage: job.set_departure(departure_time)
    # Before: departure_time is the virtual time when this job exits the system
    # After: We've set the departure time, as well as calculated the sojourn time and waiting time.
    def set_departure(self, departure_time):
        self._departure_time = departure_time
        self._sojourn_time = departure_time - self._arrival_time

    # Usage: job.set_service(service_time)
    # Before: service_time is the virtual time needed to complete the service of this job
    # After: We've set the service time, as well as initialized the remaining service time
    #        remaining service time is used for PS and other more advanced scheduling algs.
    def set_service(self, service_time):
        self._service_time = service_time
        self._remaining_service = service_time

    # Usage: job._update_remaining_service(work_done)
    # Before: work_done is the virtual time that had been 'spent' working on this job
    # After: We've updated the remaining service by subtracting the work_done
    def update_remaining_service(self, work_done):  # pragma: no cover
        self._remaining_service = self._remaining_service - work_done

    # Setter for enter service
    def set_enter_service(self, enter_service):  # pragma: no cover
        self._enter_service = enter_service
        self._waiting_time = enter_service - self._arrival_time

    # Usage: job.report_statistics(world)
    # Before: world is a global_state instance, used for this simulation
    # After: We've reported ourself to the statistics instance of this world
    def report_statistics(self, world):  # pragma: no cover
        # use self to send my statistics to the global statistic
        stats = world._stats
        stats.add_job(self)
