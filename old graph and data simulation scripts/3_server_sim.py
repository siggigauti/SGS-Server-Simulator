import os
import random
import math
from server import Server
from job import Job
from dispatcher import Dispatcher
from arrivals import PoissonArrival
from global_state import Global
from stats import Statistics
from policies import RND, ShortestQueue, SED
from job_size import Expo
from schedulers import FIFO, PS

from multiprocessing import Process

# A single simulation.
# Takes arrival rate, how many jobs to run through, how many servers and the sub_file name.
# Creates given # of servers using FCFS with expo service time of 1
# Creates a single dispatcher with JSQ policy, access to all servers.
# Arrival is Poisson
def esa_3_server(arr_rate, job_through, no_servers, file_name):
    list_of_servers = init_servers(no_servers, 1, 1)
    list_of_dispatchers = init_dispatchers(1, 2, list_of_servers)
    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(float(arr_rate))

    init_first_jobs(world, list_of_dispatchers, p_arrivals) #Create the first arrival to initiate loop

    #Main loop
    while world.next_event(): # while the virtual time of next event is less than our simulation time..
        if world._stats.number_of_jobs > job_through: # If we've reached the desired # of jobs
            data = world._stats.get_mean_sd_sojourn() #format of 'mean,sd'
            with open('./Simulation_results/esa_'+str(no_servers)+'_subfile_'+str(file_name)+'_server_test2.txt', 'a') as myfile:
                myfile.write(data+"\n")
            break
        world.process_event() # We take the event and process it (running the function(s))




def run_some_sims(lst_of_arrivals, no_of_servers, lst_of_throughput, file_name):
    i = 0
    for _ in lst_of_arrivals:
        esa_3_server(lst_of_arrivals[i], lst_of_throughput[i], no_of_servers, file_name)
        i += 1





#Creates a list from start to stop with steps of give step
def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

#returns a list of servers with given scheduler and distribution.
def init_servers(no_of_servers, server_scheduler, job_distribution):
    list_of_servers = []
    for _ in range(0, int(no_of_servers)):
        scheduler_i = FIFO() if server_scheduler == 1 else PS()
        job_size_i = Expo(job_distribution)
        server_i = Server(job_size_i, scheduler_i)
        list_of_servers.append(server_i)
    return list_of_servers

#returns a list of dispatchers with given policy and access to given servers
def init_dispatchers(no_of_dispatchers, dispatcher_policy, list_of_servers):
    list_of_dispatchers = []
    for _ in range(0, int(no_of_dispatchers)):
        policy_i = RND() if dispatcher_policy == 1 else ShortestQueue()
        dispatcher_i = Dispatcher(policy_i, list_of_servers)
        list_of_dispatchers.append(dispatcher_i)
    return list_of_dispatchers

#Takes the world, dispatchers and poisson arrival class to create initial jobs
def init_first_jobs(world, list_of_dispatchers, p_arrivals):
    for d in list_of_dispatchers:
        arrival = random.expovariate(p_arrivals._rate)
        params = [d, world]
        world.schedule_event(p_arrivals.generate_arrival, arrival, params) # Schedule the first arrivals for each dispatcher

#Function to initialize n jobs in given server
def init_server_to_state(no_of_jobs, server, scheduler_type, world):
    for _ in range(0, int(no_of_jobs)):
        job = Job(0) #All arrive at time 0
        server._total_jobs +=1
        enter_service = server._scheduler.enter_service(0, server._total_processing_time) #Takes processing time (time when server is idle) and the time of arrival. Max of those is enter service for this job
        job.set_enter_service(enter_service) #Setting the enter service, first is 0, next is 0+service_1, next is 0+service_1 + service_2.. ...
        job.set_service(server.get_service_time()) #Generates service time AND increases processing time for server
        if scheduler_type == 1: # We're using FIFO
            departure_time = job._enter_service + job._service_time # Enter service will be correct because of processing time of server bookkeeping
            job.set_departure(departure_time) #Set the departure time as enter service+service time. (Its a timeperiod on the timeline)
            world.schedule_event(server.departure, job._departure_time, [job, world]) #Schedule this departure to the world queue



def c(no_servers, arrivals):
    rho = arrivals/no_servers
    c = no_servers
    div_sum = 0
    for k in range(0, c):
        div_sum += math.pow((c*rho),k)/math.factorial(k)
    middle = math.factorial(c)/math.pow((c*rho),c)
    under = (1 + (1 - rho) * middle * div_sum)
    fin_c = (1 / under)

    return (((rho/(1-rho)) * fin_c +c*rho)/arrivals)

def split_list(a_list):
    half = math.floor(len(a_list)/2)
    return a_list[:half], a_list[half:]

if __name__ == '__main__':
    #create a list of arrivals (split into two)
    arrivals = drange(0.01, 2.95, 0.03) 
    lst_arrivals = []
    for x in arrivals:
        lst_arrivals.append(x)
    #create a list of throughputs (split into two)
    lst_throughput = []
    for _ in lst_arrivals:
        lst_throughput.append(math.pow(10,6))

    run_some_sims(lst_arrivals, 3, lst_throughput, '3_server_1Mil_test')
