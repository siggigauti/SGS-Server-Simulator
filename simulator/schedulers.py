# A general scheduler structure.
from heapq import heappush
from heapq import heappop
# Used for dictating 'must-have' methods for each type of scheduler


class Scheduler():
    def __init__(self, *args, **kwargs):  # pragma: no cover
        pass

    def schedule(self, job, server_queue):  # pragma: no cover
        pass

    def enter_service(self, time, next_idle):  # pragma: no cover
        pass


# A FIFO scheduler.
class FIFO(Scheduler):
    def __init__(self, *args, **kwargs):
        pass
        # check type input, and calls a method to set that type as attributes of the instance
        # e.g. if type = FCFS, then method called to put meta info in attributes of instance.

    # Usage: scheduler.schedule(job, server_queue)
    # Before: job is a Job instance meant to be scheduled. Server_queue is the servers_queue of jobs
    # After: We've set the departure time the given job, as well as any other jobs that may have finished.
    def schedule(self, job, server_queue, prev_arrival):
        departure_time = job._enter_service + job._service_time  # Enters service and then gets work, then departs
        job.set_departure(departure_time)  # Setting the departure time, as well as waiting and sojourn.
        return [[job], server_queue]  # Return a list of jobs to be scheduled for departure

    def enter_service(self, time, next_idle):
        return max(next_idle, time)  # Either now (there are no jobs) or next time it's idle


# A PS scheduler, takes care of the prio heap for his server and is responsible for updating the
# jobs when a new arrival comes, extend the departure time e.t.c.
# Takes care of departures by placing them in the global scheduler when job leaves. (or place in stats)
class PS(Scheduler):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        pass
    # Similar as FIFO, has method schedule(...):
    # which takes new arrival, does checks on the heap(queue of server)
    # and makes neccessary departures and updates for jobs

    def schedule(self, job, server_queue, prev_arrival):
        curr_arrival = job._arrival_time
        jobs_to_depart = []
        no_of_jobs = len(server_queue)
        delta_change = curr_arrival - prev_arrival  # The amount of time between the two arrivals
        while server_queue:
            time, job_x = heappop(server_queue)
            if time <= delta_change / no_of_jobs:  # if the remaining service was less than the time between the last arrival and now
                # Then we can pop this even off the server queue and place it in departure list
                jobs_to_depart.append(job_x)
                # !!!! Update the departure time of this job!
                job_x._work_done += time

                job_x.set_departure(job_x._work_done + job_x._arrival_time)
                for job_s in server_queue:  # update remaining jobs
                    job_s[0] -= time  # remove the worked time from each remaining service.
                    job_s[1]._work_done += time
                delta_change -= (time * no_of_jobs)  # remove worked time from delta_change for next iteration
                no_of_jobs -= 1  # remove job from the 'n'
            else:
                # recalculate the remaining service on all jobs and create a new server_queue
                heappush(server_queue, [time, job_x])  # the job popped was not finished.
                work_done = delta_change / no_of_jobs  # calculate work done on each job
                for job_s in server_queue:  # for each job that did not depart
                    job_s[0] -= work_done  # update the remaining service by the work done.
                    job_s[1]._work_done += work_done
                break
        heappush(server_queue, [job._service_time, job])

        return [jobs_to_depart, server_queue]

    def enter_service(self, time, next_idle):
        return time  # Goes into service immediately


class Agent(Scheduler):
    pass
