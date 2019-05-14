#Script to start running a simulation.
import os
import random
import math
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from simulator.server import Server
from simulator.job import Job
from simulator.dispatcher import Dispatcher
from simulator.arrivals import PoissonArrival
from simulator.global_state import Global
from statistics_and_graphs.stats import Statistics
from simulator.policies import RND, ShortestQueue, SED, Qlearning
from simulator.job_size import Expo
from simulator.schedulers import FIFO, PS
from statistics_and_graphs.auto_graphs import AutoGraphs
import numpy as np
import matplotlib.pyplot as plt
import threading
import ast
import time

#A function to clear the screen
def clear():
    #Checks if windows or other.
    os.system("cls" if os.name == "nt" else "clear")

final_data = [] #Used to store data for reach_box simulation

def start_screen():
    clear()
    print("Welcome to trix-simulation #BETA#")
    print("1. Sim for a given time.")
    print("2. Sim for a given time from starting state.")
    print("3. Sim from a given state until sim reaches box boundry.")
    print("4. Sim from a given n+1, n state until sim goes back to n,n box.")
    type_of_sim = input("Choose a simulation type > ")
    type_of_sim = int(type_of_sim)
    if type_of_sim == 1:
        sim_type_1()
    elif type_of_sim == 2:
        sim_type_2()
    elif type_of_sim == 3:
        sim_type_3()
    elif type_of_sim == 4:
        sim_type_4()
    elif type_of_sim == 5:
        testing_3_server()
    else:
        print("Did not pick a type, (1, 2, 3 or 4).")

def sim_type_1():
    clear()
    print("You picked to simulate for a given time.")
    no_of_servers       = input("How many servers > ")
    server_scheduling   = input("What scheduling algorithm? (1 for FIFO, 2 for PS) > ")
    job_distribution    = input("What service rate for each server? > ")
    no_of_dispatchers   = input("How many dispatchers > ")
    dispatcher_policy   = input("What dispatcher policy (1 for RND, 2 for JSQ) > ").upper()
    arrival_rate        = input("What arrival rate would you like? > ")
    sim_time            = input("How long do you want the simulation to be? > ")
    start_simulation(no_of_servers, server_scheduling, no_of_dispatchers, dispatcher_policy, arrival_rate, job_distribution, sim_time)

def sim_type_2():
    clear()
    print("You picked to simulate from a given state for a given time.")
    print("This simulation will have 2 servers and 1 dispatcher using JSQ.")
    jobs_in_server_1    = input("How many jobs in server 1 initially? > ")
    jobs_in_server_2    = input("How many jobs in server 2 initially? > ")
    scheduler           = input("Scheduler type (1 for FIFO, 2 for PS)? > ")
    arrival_rate        = input("What arrival rate (lambda)? > ")
    service_rate        = input("The service rate is exponential, what rate? > ")
    sim_time            = input("How long is the simulation? > ")
    start_simulation_sim_time(jobs_in_server_1, jobs_in_server_2, arrival_rate, service_rate, sim_time, scheduler)

def sim_type_3():
    clear()
    print("You picked to simulate a run from a given state until one of the server reaches some boundry")
    print("This is a 2 server simulation from a given starting state")
    print("This simulation uses one dispatcher using JSQ policy")
    print("Stats will be written to file for each reset, into folder Simulation_results under name:")
    print("given_end_of_'given_x'_and_'given_y'. E.g. given_end_of_8_and_4.txt")
    no_of_jobs_server_1     = input("How many jobs initially in server 1 > ")
    no_of_jobs_server_2     = input("How many jobs initially in server 2 > ")
    scheduler               = input("Scheduler type (1 for FIFO, 2 for PS)? > ")
    arrival_rate            = input("What arrival rate would you like? > ")
    service_rate            = input("What service rate (expo)? > ")
    sim_time                = input("How long is this simulation? > ")
    given_x                 = input("What is the desired boundry state for server 1? > ")
    given_y                 = input("What is the desired boundry state for server 2? > ")
    start_simulation_state(no_of_jobs_server_1, no_of_jobs_server_2, arrival_rate, service_rate, given_x, given_y, sim_time, scheduler)

def sim_type_4():
    clear()
    print("You picked simulation start from n+1, n until both servers reach state <= n")
    print("Here we have 2 servers, 1 dispatcher with JSQ.")
    print("This simulation type will run many simulations, with arrivals varying from 0.1 to 1.9.")
    print("The service rate is 1 for each server, and for each arrival rate, we will push through around 100K to 10M jobs")
    print("Stats will be written to file with the arrival rate concatenated to the back of the filename.")
    print("All stats will be printed to file in Simulation_results folder.")
    given_n = input("What n would you like (e.g. 4) for the starting state of (n+1, n) > ")
    sim_timeout = input("What is the timeout? (each simulation will run for max this amount of time before timing out) > ")
    scheduler = input("What scheduling algorithm (1 for FIFO, 2 for PS)? > ")
    name_of_file = input("What would you like the names of the files to be ? e.g. name_of_file_[arrival_rate].txt > ")
    print("Starting simulation, this may take a while...")
    start_sim_less_than(given_n, sim_timeout, name_of_file, scheduler)

# Simulation function to run a simulation for a given time.
def start_simulation(no_of_servers, server_scheduler, no_of_dispatchers, dispatcher_policy, arrival_rate, job_distribution, sim_time):
    list_of_servers = init_servers(no_of_servers, server_scheduler, job_distribution)
    list_of_dispatchers = init_dispatchers(no_of_dispatchers, dispatcher_policy, list_of_servers, [])
    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(float(arrival_rate)/len(list_of_dispatchers))
    init_first_jobs(world, list_of_dispatchers, p_arrivals)
    #Main loop
    for x in range(1, 101):
        while world.next_event() <= float(sim_time)*(x*0.01): # while the virtual time of next event is less than our simulation time..
            world.process_event() # We take the event and process it (running the function(s))
        world._stats.write_to_file_jobs()
        print("{}%".format(x))

    total_no_jobs = world._stats.number_of_jobs
    print(total_no_jobs)
    world._stats.print_stats()
    save_stats(world) #Ask user if he wants to save stats to file

# Simulation function to run a simulation for a given time from a given state.
def start_simulation_sim_time(no_of_jobs_server_1, no_of_jobs_server_2, arrival_rate, job_distribution, sim_time, scheduler):
    list_of_servers = init_servers(2, scheduler, job_distribution)
    policy_i = ShortestQueue() #Join shortest queue policy
    dispatcher = Dispatcher(policy_i, list_of_servers) #Create a dispatcher with JSQ policy
    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(float(arrival_rate))

    init_server_to_state(no_of_jobs_server_1, list_of_servers[0],scheduler,world)
    init_server_to_state(no_of_jobs_server_2, list_of_servers[1],scheduler,world)
    init_first_jobs(world,[dispatcher], p_arrivals)

    world.number_of_arr_dep = 0 #resetting the number of events before we start
    for x in range(1, 11):
        # Now that each dispatcher has an arrival, we can start looping through events
        while world.next_event() <= float(sim_time)*(x*0.1): # while the virtual time of next event is less than our simulation time..
            world.process_event() # We take the event and process it (running the function(s))
        print("{}%".format(x*10))
    #for loop to step between while loops (every 10%)while world.next

    total_no_jobs = world._stats.number_of_jobs
    print(total_no_jobs)
    world._stats.print_stats()
    save_stats(world)

# Simulation function to run a simulation from given state until it reaches the boudries of its box, then resets itself.
def start_simulation_state(no_of_jobs_server_1, no_of_jobs_server_2, arrival_rate, job_distribution, given_x, given_y, sim_time, scheduler):
    list_of_servers = init_servers(2,scheduler,job_distribution)
    policy_i = ShortestQueue() #Join shortest queue policy
    dispatcher = Dispatcher(policy_i, list_of_servers) #Create a dispatcher with JSQ policy
    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(float(arrival_rate)) 
    
    def reset_world(first_arrival):
        nonlocal list_of_servers, dispatcher, statistics, world # if we want to modify variable from closure, must place as nonlocal
        list_of_servers.clear() #clear the 2 servers
        list_of_servers = init_servers(2, scheduler, job_distribution)
        dispatcher = Dispatcher(policy_i, list_of_servers) # resetting the dispatcher with new servers
        statistics = Statistics()
        world = Global(statistics)
        init_server_to_state(no_of_jobs_server_1, list_of_servers[0], scheduler, world)
        init_server_to_state(no_of_jobs_server_2, list_of_servers[1], scheduler, world)
        params = [dispatcher, world]
        world.schedule_event(p_arrivals.generate_arrival, first_arrival, params) #Schedule first arrival to start chain

    reset_world(0) # Call function to setup our world

    # Now we need to schedule the initial arrivals to start the chain of events.
    for x in range(1, 11):
        # Now that each dispatcher has an arrival, we can start looping through events
        while world.next_event() <= float(sim_time)*(x*0.1): # while the virtual time of next event is less than our simulation time..
            if list_of_servers[0]._total_jobs > int(given_x) or list_of_servers[1]._total_jobs > int(given_y):
                next_arrival_new_world = world.next_event() #Get the time for the first event for new world
                world._stats.write_to_file_intermediate_stats('given_end_of_'+given_x+'_and_'+given_y)
                reset_world(next_arrival_new_world) # This function should reset statistics, world event queue, and server states
            world.process_event() # We take the event and process it (running the function(s))
        print("{}%".format(x*10))
    #for loop to step between while loops (every 10%)while world.next

    total_no_jobs = world._stats.number_of_jobs
    print(total_no_jobs)
    world._stats.print_stats()
    save_stats(world)

# Initial sim function to run a simulation from given state n+1, n, until it reaches both x,y <= n (goes back into box)
# Pushes a given number of jobs through the system as minimum.
def start_sim_less_than(given_n, sim_timeout, name_of_file, scheduler):

    lst = drange(0.01, 3, 0.01)
    y = 0
    global jobs_ran
    #lst_jobs_through_system = [math.pow(10,5), math.pow(10,5), math.pow(10,5), math.pow(10,5), math.pow(10,5), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,7), math.pow(10,7), math.pow(10,7)]
    x_jobs = []
    tracker = 0
    lst_len = 0
    for _ in range(0,300): # loop through all the numbers
        if tracker <= 150:
            x_jobs.append(math.pow(10,6))
        elif tracker <= 200:
            x_jobs.append(math.pow(10,7))
        elif tracker <= 300:
            x_jobs.append(math.pow(10,8))
        tracker += 1
    for x in lst: #from 0.1 to 1.9 with 0.1 step-wise
        jobs_ran = 0
        final_data.clear()
        while jobs_ran<x_jobs[y]:
            start_simulation_less_than_n(int(given_n)+1,int(given_n),x,1,int(sim_timeout), int(scheduler))
        y += 1
        with open('./Simulation_results/'+name_of_file+"_"+str(round(x,2))+'.txt', 'a') as myfile:
            for line in final_data:
                data = "{0},{1},{2:<8.5f},{3}".format(line[0], line[1], line[2], line[3])
                myfile.write(data+"\n")
        print("Finished with step: {}".format(round(x,2)))

def start_simulation_less_than_n(no_of_jobs_server_1, no_of_jobs_server_2, arrival_rate, job_distribution, sim_time, scheduler):
    list_of_servers = init_servers(3,scheduler,job_distribution)
    global jobs_ran
    global final_data
    stopping_n = no_of_jobs_server_2 
    # Create dispatcher
    policy_i = ShortestQueue() #Join shortest queue policy
    dispatcher = Dispatcher(policy_i, list_of_servers) #Create a dispatcher with JSQ policy
    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(float(arrival_rate))
    arrival = 0

    init_server_to_state(no_of_jobs_server_1,list_of_servers[0],scheduler,world)
    init_server_to_state(no_of_jobs_server_2,list_of_servers[1],scheduler,world)
    init_server_to_state(no_of_jobs_server_2,list_of_servers[2],scheduler,world)
    
    initial_arrival = random.expovariate(p_arrivals._rate)
    params = [dispatcher, world]
    world.schedule_event(p_arrivals.generate_arrival, initial_arrival, params) #Schedule first arrival to start chain
    last_event = 0
    world.number_of_arr_dep = 0 #resetting the number of events before we start
    # Now we need to schedule the initial arrivals to start the chain of events.
    # Now that each dispatcher has an arrival, we can start looping through events
    while world.next_event() <= float(sim_time): # while the virtual time of next event is less than our simulation time..
        if(list_of_servers[0]._total_jobs<=stopping_n and list_of_servers[1]._total_jobs <= stopping_n and list_of_servers[2]._total_jobs <= stopping_n):
            break
        last_event = world.next_event()
        world.process_event() # We take the event and process it (running the function(s))
    #for loop to step between while loops (every 10%)while world.next
    #We've reached a stopping state. Record event parameters and print to file
    jobs_ran += world._stats.number_of_jobs # We stopped, we add the number of jobs ran this time to global variable
    recorded_x = list_of_servers[0]._total_jobs
    recorded_y = list_of_servers[1]._total_jobs
    recorded_T = last_event #Last event that happened (e.g. departure that caused the total jobs to be < 4)
    recorded_N = world.number_of_arr_dep #Get the number of events that happened'
    final_data.append((recorded_x, recorded_y, recorded_T, recorded_N))

def testing_3_server(x_jobs, y, lst, file_name):
    #first 3 servers
    for x in lst:
        esa_3_server(x,x_jobs[y],3, file_name)
        y += 2

def testin_4_server():
    lst = drange(0.04, 4, 0.04)
    tracker = 0
    x_jobs = []
    y = 0
    for _ in range(0,80): # loop through all the numbers
        if tracker <= 30:
            x_jobs.append(math.pow(10,6))
        elif tracker <= 60:
            x_jobs.append(math.pow(10,7))
        elif tracker <= 80:
            x_jobs.append(math.pow(10,8))
        tracker += 1
    for x in lst:
        esa_3_server(x,x_jobs[y],4)
        y += 1

def esa_3_server(arr_rate, job_through, no_servers, file_name):
    list_of_servers = init_servers(no_servers, 1, 1)
    list_of_dispatchers = init_dispatchers(1, 2, list_of_servers, [])
    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(float(arr_rate))
    init_first_jobs(world, list_of_dispatchers, p_arrivals)
    #Main loop
    while world.next_event(): # while the virtual time of next event is less than our simulation time..
        if world._stats.number_of_jobs > job_through:
            data = world._stats.get_mean_sd_sojourn() #format of 'mean,sd'
            with open('./Simulation_results/esa_'+str(no_servers)+'_subfile_'+str(file_name)+'_server_test.txt', 'a') as myfile:
                myfile.write(data+"\n")
            break
        world.process_event() # We take the event and process it (running the function(s))

#Creates a list from start to stop with steps of give step
def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

#returns a list of servers with given schedulers and distributions.
def init_servers(no_of_servers, server_scheduler, job_distribution):
    list_of_servers = []
    for i in range(int(no_of_servers)):
        scheduler_i = FIFO() if server_scheduler[i] == 1 else PS()
        job_size_i = Expo(job_distribution[i])
        server_i = Server(job_size_i, scheduler_i)
        list_of_servers.append(server_i)
    return list_of_servers

#returns a list of dispatchers with given policy and access to given servers
def init_dispatchers(no_of_dispatchers, dispatcher_policy, list_of_servers, qlearn):
    list_of_dispatchers = []
    for _ in range(0, int(no_of_dispatchers)):
        if dispatcher_policy == 1:
            policy_i = RND()
        elif dispatcher_policy == 2:
            policy_i = ShortestQueue()
        elif dispatcher_policy == 3:
            policy_i = Qlearning(qlearn[0], qlearn[1], qlearn[2], qlearn[3], list_of_servers)
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

#Function to save stats to file
def save_stats(world):
    save_stats          = input("Do you want to save these stats to file Y/N?").upper()
    if save_stats == 'Y':
        file_name        = input("What name for the file? > ")
        print("Thank you, your stats will be saved in the Simulation_results directory.")
        world._stats.write_to_file_stats(file_name)


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
#start_screen()

def not_needed():
    lst = drange(0.01, 3, 0.01)
    tracker = 0
    x_jobs = []
    brk = 260
    count = 1
    for x in lst:
        if count == brk:
            break
        count +=1

    y = count
    for _ in range(0,300): # loop through all the numbers
        if tracker <= 100:
            x_jobs.append(math.pow(10,6))
        elif tracker <= 250:
            x_jobs.append(math.pow(10,7))
        elif tracker <= 300:
            x_jobs.append(math.pow(10,8))
        tracker += 1
    lst2 = []
    for x in lst:
        lst2.append(round(x,2))

    lst3 = lst2[::2]
    lst4 = lst2[1::2]
    #Hold the rest of the numbers each, only half.
    # y holds the count of x_jobs list

    #These now start from 260, first odd is 261, first even is 260 e.t.c.
    p = Process(target = testing_3_server, args=(x_jobs, y, lst3, 'even'))
    p.start()
    p2 = Process(target = testing_3_server, args=(x_jobs, y+1, lst4, 'odd'))
    p2.start()
    p.join()
    p2.join()

def diff_between_real_and_sims():
    mmc_queue = []
    arrivals = drange(0.01, 2.95, 0.03)
    for x in arrivals:
        mmc_queue.append(c(3,x))
    
    simulated_means = []
    lines = []
    with open('./Simulation_results/esa_3_subfile_3_server_1Mil_test_server_test2.txt') as f:
        lines = f.read().splitlines()
    for line in lines:
        print(line)
        x = line.split(',')
        print(x[0])
        simulated_means.append(x[0])

    graph_means = []
    i = 0
    for _ in simulated_means:
        graph_means.append(float(simulated_means[i])/mmc_queue[i])
        i += 1

    f = open('3_server_1mil.txt', 'a+')
    for item in graph_means:
        f.write(str(item)+"\n")
    f.close()
    graph = AutoGraphs('3_server_1mil')
    graph.create_line_graph()

def print_matrices_q(list_of_dispatchers, x):
    Q_policy = list_of_dispatchers[0]._policy
    action_matrix = []
    cost_matrix = []
    for j in range(Q_policy.S[0],-1,-1): #Go through all col
        action_row = [] #initialize the row
        cost_row = []
        for i in range(0, Q_policy.S[1]+1): #Go through every row 
            kval = Q_policy.Q[str(([i,j],0))] #initialize the first 'choice' as best ##subfunction to map for values
            kmin = 0 #which server was best 
            for k in range(1, Q_policy.n_servers): #For this state, go through all the server paths it can take and find best
                if kval > Q_policy.Q[str(([i,j],k))]: #if this new server has a better value  ##subfunction to map for values
                    kval = Q_policy.Q[str(([i,j],k))]  # (s,k)
                    kmin = k #index
            action_row.append(kmin) #Adding the value to the row
            cost_row.append(kval)
        action_matrix.append(action_row) #The row has been added.
        cost_matrix.append(cost_row)
    #print('Action matrix')
    #for i in action_matrix:
    #    print(['%.6f' % j for j in i])

    #print('Cost matrix')
    #for i in cost_matrix:
    #    print(['%.6f' % j for j in i])
    #cost_matrix = np.array(cost_matrix)
    #action_matrix = np.array(action_matrix)
    with open('./sim_data_qlearn/v2matrix_2Mjobs_RND.txt', 'a') as f: #make unique with date/time tag
        f.write('\n{} percentage\n'.format(x))
        f.write('Action matrix:\n')
        for i in action_matrix:
            for j in i:
                f.write('%.6f ' % j)
            f.write('\n')
        f.write('Cost matrix:\n')
        for i in cost_matrix:
            for j in i:
                f.write('%.6f ' % j)
            f.write('\n')

def q_testing():
    sim_time = 100000
    list_of_servers = init_servers(2, [1,1], [1,1]) # 2 servers, both using FIFO and mui = 1
    list_of_dispatchers = init_dispatchers(1, 3, list_of_servers, [[4,4],[],[], sim_time]) # 1 dispatcher, Qlearn, 5x5 box, nothing excluded.
    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(1) # Poisson arrivals with 1 arrival rate.
    init_first_jobs(world, list_of_dispatchers, p_arrivals)
    #Main loop

    for x in range(1, 101):
        while world.next_event() <= float(sim_time)*(x*0.01): # while the virtual time of next event is less than our simulation time..
            world.process_event() # We take the event and process it (running the function(s))
        #world._stats.write_to_file_jobs()
        print("{}%".format(x))

    total_no_jobs = world._stats.number_of_jobs
    print(total_no_jobs)
    print('The Q: '+ str(list_of_dispatchers[0]._policy.Q))
    v = list_of_dispatchers[0]._policy.v
    v2 = list_of_dispatchers[0]._policy.v2
    print('mean cost rate r: '+str(list_of_dispatchers[0]._policy.r))
    print('The v:')
    i = 0
    for key in v:
        i+=1
        print(str(key)+': '+str(v[key])+'  ')
        if not i % 5:
            print('\n') 
    print('The v2:')
    i = 0
    for key in v2:
        i+=1
        print(str(key)+': '+str(v2[key])+'\n')
        if not i % 5:
            print('\n')
    world._stats.print_stats()
    save_stats(world) #Ask user if he wants to save stats to file

#Used for threading


def q_testing_id(id):
    sim_time = 2000000
    list_of_servers = init_servers(2, 1, 1) # 2 servers using FIFO and mui = 1
    list_of_dispatchers = init_dispatchers(1, 3, list_of_servers, [[4,4],[],[], sim_time]) # 1 dispatcher, Qlearn, 5x5 box, nothing excluded.
    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(1) # Poisson arrivals with 1 arrival rate.
    init_first_jobs(world, list_of_dispatchers, p_arrivals)
    #Main loop

    for x in range(1, 101):
        while world.next_event() <= float(sim_time)*(x*0.01): # while the virtual time of next event is less than our simulation time..
            world.process_event() # We take the event and process it (running the function(s))
        #world._stats.write_to_file_jobs()
        print("thread id: {}, finised {}%".format(id,x))
        if(x%5 == 0):
            print_matrices_q(list_of_dispatchers, x)
            v2 = list_of_dispatchers[0]._policy.v2
            with open('./TDlearn/2Mjobs_V2_per5_RND_'+str(id)+'.txt', 'a') as f:
                for key in v2:
                    f.write(str(key)+': '+str(v2[key])+'\n')
                f.write('\n')

def get_min_value(values):
    indxs = []
    for indx, item in enumerate(values):
        if item == min(values):
            indxs.append(indx)
    return random.choice(indxs)

def fraction_correct():
    all_data = []
    for i in range(0,20):
        with open('./TDlearn/2Mjobs_V2_per5_RND_'+str(i)+'.txt', 'r') as f:
            data = [float(i[8:]) for i in f.read().splitlines()[:-1] if i != '']
        all_data.append(data)
    #All data is of form:
    # [[       ]
    #  [       ]
    #  .........
    #  [       ]]
    #####
    #Where each row is a full simulation (20 of them)
    #each row: state{s1,s2} its the value at that state
    #[ {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4}        for the 5% mark
    #  {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4}        10%
    #  ....                                                       15%, 20%, ...
    #  {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4} ]      100%

    RND_value_matrix = []
    for i in range(0,5):
        for j in range(0,5):
            RND_value_matrix.append((i*(i+1) + j*(j+1)))
    MSE = 0
    mean_simulation = [0.0]*500
    for sim in all_data:#There are 20 simulations
        mean_simulation = [sum(i) for i in zip(sim, mean_simulation)]
    mean_simulation = [i/20 for i in mean_simulation]
    percent_data = [mean_simulation[x:x+25] for x in range(0, len(mean_simulation), 25)]
    #Percent_data holds a list of V2 for each percentage.
    frac_correct = [] 
    #-1 either, 0 server1,  1 server 2
    correct_decisions = {}
    for i in range(5):
        for j in range(5):
            if i == j:
                correct_decisions[str([i,j])] = -1
            elif i < j:
                correct_decisions[str([i,j])] = 0
            else:
                correct_decisions[str([i,j])] = 1
    for snapshot in percent_data:
        v2 = {}
        snapshot_accuracy = []
        k = 0
        for i in range(5):
            for j in range(5):
                v2[str([i,j])] = snapshot[k]
                k +=1
        for key, val in v2.items():
            if correct_decisions[key] == -1:
                continue
            if ast.literal_eval(key)[0] == 4:
                continue
            if ast.literal_eval(key)[1] == 4:
                continue
            values = []
            for j in range(2): # Step in every direction
                dx = ast.literal_eval(key) # copy state x
                dx[j] += 1   # dx = new state in direction j
                values.append(v2[str(dx)]) #Add the value function for that step
            k = values.index(min(values)) #returns 0 or 1. 0 if server 0 is 'better' and will be the choice for this state.
            print(k)
            if k == correct_decisions[key]:
                snapshot_accuracy.append(1) #correct decision was made by the V2
            else:
                snapshot_accuracy.append(-1) #incorrect
        fraction_of_correct_dec = (snapshot_accuracy.count(1)/len(snapshot_accuracy)) #number of 1's divided by total count.
        frac_correct.append(fraction_of_correct_dec)
    print(frac_correct)

def q_testing_frac_1per():
    sim_time = 20000
    list_of_servers = init_servers(2, 1, 1) # 2 servers using FIFO and mui = 1
    list_of_dispatchers = init_dispatchers(1, 3, list_of_servers, [[4,4],[],[], sim_time]) # 1 dispatcher, Qlearn, 5x5 box, nothing excluded.
    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(1) # Poisson arrivals with 1 arrival rate.
    init_first_jobs(world, list_of_dispatchers, p_arrivals)
    #Main loop
    all_v2 = [] 
    for x in range(1, 101):
        while world.next_event() <= float(sim_time)*(x*0.01): # while the virtual time of next event is less than our simulation time..
            world.process_event() # We take the event and process it (running the function(s))
        all_v2.append(list_of_dispatchers[0]._policy.v2.copy()) #Want only the copy at this time
    
    return all_v2

def threading_jsq_accuracy(iter_num, all_jsq_data):
    correct_decisions = {}
    for i in range(5):
        for j in range(5):
            if i == j:
                correct_decisions[str([i,j])] = -1
            elif i < j:
                correct_decisions[str([i,j])] = 0
            else:
                correct_decisions[str([i,j])] = 1

    for i in range(iter_num):
        all_v2 = q_testing_frac_1per()
        fraction_of_correct_dec = []
        for v2 in all_v2:
            snapshot_accuracy = []
            for key, val in v2.items():
                if correct_decisions[key] == -1:
                    continue
                if ast.literal_eval(key)[0] == 4:
                    continue
                if ast.literal_eval(key)[1] == 4:
                    continue
                values = []
                for j in range(2): # Step in every direction
                    dx = ast.literal_eval(key) # copy state x
                    dx[j] += 1   # dx = new state in direction j
                    values.append(v2[str(dx)]) #Add the value function for that step
                k = values.index(min(values)) #returns 0 or 1. 0 if server 0 is 'better' and will be the choice for this state.
                if k == correct_decisions[key]:
                    snapshot_accuracy.append(1) #correct decision was made by the V2
                else:
                    snapshot_accuracy.append(-1) #incorrect
            fraction_of_correct_dec.append(snapshot_accuracy.count(1)/len(snapshot_accuracy)) #number of 1's divided by total count.
        all_jsq_data.append(fraction_of_correct_dec)
        
def plot_frac_correct():
    start = time.clock()
    iter_number = 200
    all_jsq_accuracy_test_data = []
    all_processes = []
    threading_jsq_accuracy(iter_number, all_jsq_accuracy_test_data)

    print(all_jsq_accuracy_test_data)
    mean_jsq_accuracy = [0]*100
    for jsq_data in all_jsq_accuracy_test_data:
        mean_jsq_accuracy = [sum(i) for i in zip(jsq_data, mean_jsq_accuracy)]
    mean_jsq_accuracy = [i/iter_number for i in mean_jsq_accuracy]
    end = time.clock()
    print('time elapsed: {}'.format(end-start))
    print(len(mean_jsq_accuracy))
    plt.plot(mean_jsq_accuracy)
    plt.xlabel('Number of jobs completed')
    plt.ylabel('Accuracy compared to JSQ')
    xs = np.linspace(200, 20000, 11).astype(int)
    plt.xticks(range(0,101,10), xs, rotation='vertical')
    plt.tight_layout()
    plt.show()  

def q_heterogeneous():
    sim_time = 1000000 #Job required to get aprox good V2 matrix
    list_of_servers = init_servers(2, [1,1], [3,1]) 
    list_of_dispatchers = init_dispatchers(1, 3, list_of_servers, [[12,4],[],[], sim_time]) # 1 dispatcher, Qlearn, 5x5 box, nothing excluded.
    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(3) # Poisson arrivals with arrival rate 3: Load 75% because we have 4 consumptions per time unit.
    init_first_jobs(world, list_of_dispatchers, p_arrivals)
    #Main loop

    for x in range(1, 101):
        while world.next_event() <= float(sim_time)*(x*0.01): # while the virtual time of next event is less than our simulation time..
            world.process_event() # We take the event and process it (running the function(s))
        #world._stats.write_to_file_jobs()
        print("{}%".format(x))

    v2 = list_of_dispatchers[0]._policy.v2
    with open('./data_results/Spring_paper_figures/v2matrix_500k_jobs.txt', 'a') as f:
        for key in v2:
            f.write(str(key)+': '+str(v2[key])+'\n')
        f.write('\n')
    world._stats.print_stats()


def plot_action_from_matrix(filename):
    matrix = {}
    plottin_matrix = np.empty([0,4])
    lines = None
    with open('../'+filename, 'r') as f:
        lines = f.read().splitlines()[:-4]
    lines = [(i.split(': ')) for i in lines]
    for line in lines:
        matrix[line[0]] = float(line[1])
    #plotting matrix, 1 entry for picking server 1, 0 entry for picking server 0
    row_counter = 0
    row = []
    for key, value in matrix.items():
        if ast.literal_eval(key)[0] == 12:
            continue
        if ast.literal_eval(key)[1] == 4:
            continue
        values = []
        for j in range(2): # Step in every direction
            dx = ast.literal_eval(key) # copy state x
            dx[j] += 1   # dx = new state in direction j
            values.append(matrix[str(dx)]) #Add the value function for that step
        k = values.index(min(values)) #returns 0 or 1. Ties in random
        row.append(k)
        row_counter +=1
        if row_counter == 4:
            plottin_matrix = np.vstack((plottin_matrix, row))
            row = [] #empty the row
            row_counter = 0 #empty counter
    print(np.rot90(plottin_matrix,1))
    #plottin_matrix = np.rot90(plottin_matrix,1)
    plt.imshow(plottin_matrix.T, origin='lower')
    ax = plt.gca()
    ax.set_xticks(np.arange(-.5, 12, 1))
    ax.set_yticks(np.arange(-.5, 4, 1))
    ax.set_xticklabels(np.arange(0, 12, 1))
    ax.set_yticklabels(np.arange(0, 4, 1))
    plt.grid(which='major', axis='both', linestyle='-')
    plt.title('Offered load = 0.75')
    plt.xlabel('Number of jobs in server 2')
    plt.ylabel('Number of jobs in server 1')
    plt.show()

if __name__ == '__main__':
    #plot_action_from_matrix('./data_results/Spring_paper_figures/v2matrix_500k_jobs.txt')
    q_testing()

    



def plotting_MSE():
    all_data = []
    for i in range(0,20):
        with open('./data_results/TDlearn/2Mjobs_V2_per5_RND_'+str(i)+'.txt', 'r') as f:
            data = [float(i[8:]) for i in f.read().splitlines()[:-1] if i != '']
        all_data.append(data)
    #All data is of form:
    # [[       ]
    #  [       ]
    #  .........
    #  [       ]]
    #####
    #Where each row is a full simulation (20 of them)
    #each row: state{s1,s2} its the value at that state
    #[ {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4}        for the 5% mark
    #  {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4}        10%
    #  ....                                                       15%, 20%, ...
    #  {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4} ]      100%

    RND_value_matrix = []
    for i in range(0,5):
        for j in range(0,5):
            RND_value_matrix.append((i*(i+1) + j*(j+1)))
    MSE = 0
    mean_simulation = [0.0]*500
    for sim in all_data:#There are 20 simulations
        mean_simulation = [sum(i) for i in zip(sim, mean_simulation)]
    mean_simulation = [i/20 for i in mean_simulation]
    percent_data = [mean_simulation[x:x+25] for x in range(0, len(mean_simulation), 25)]

    plt_data = []
    for prc_data in percent_data:
        plt_data.append((sum(math.pow(o[0]-o[1], 2) for o in zip(prc_data, RND_value_matrix)))/len(RND_value_matrix))
    print(plt_data)

    plt.plot([i for i in range(5, 101, 5)], plt_data)
    plt.show()