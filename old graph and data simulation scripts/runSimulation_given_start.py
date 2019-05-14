#Script to start running a simulation.
import os
import random
import math
from server import Server
from job import Job
from dispatcher import Dispatcher
from arrivals import PoissonArrival
from global_state import Global
from stats import Statistics
from policies import RND, ShortestQueue
from job_size import Expo
from schedulers import FIFO
#A function to clear the screen
def clear():
    #Checks if windows or other.
    os.system("cls" if os.name == "nt" else "clear")

final_data = [] #Used to store data for reach_box simulation
def start_screen():
    clear()
    print("Welcome to trix-simulation #BETA#")
    print("The next input will define what simulation type you want to run.")
    print("You can choose between SIM, STATE, and REACH_BOX with 1, 2 or 3 respectively.")
    print("All of these run on a 2 server system with 1 dispatcher and JSQ.")
    print("All of these also allow you can define how many jobs are initially in the system for each server")
    print("In SIM AND STATE you can define arrival rate and service rate, as well as sim time.")
    print("In REACH_BOX, you define a (n+1, n) initial state then sim will run until both servers have <= n jobs.")
    sim_type = input("Now, what simulation type do you want? > ").upper()
    if sim_type == '1' or sim_type == '2':
        start_screen_2()
    elif sim_type == '3':
        start_screen_1()
def start_screen_2():
    clear()
    sim_or_state = True
    print("Welcome to trix-simulation #BETA#")
    print("This is a 2 server simulation from a given starting state")
    print("This simulation uses one dispatcher using JSQ policy")
    no_of_jobs_server_1     = input("How many jobs in server 1 > ")
    no_of_jobs_server_2     = input("How many jobs in server 2 > ")
    arrival_rate            = input("What arrival rate would you like? > ")
    job_distribution        = input("What job distribution (only expo supported, provide service rate)? > ")
    sim_time                = input("How long is this simulation? > ")
    while(sim_or_state):
        sim_or_reach_state      = input("Write SIM to do a simulation for x time units, write STATE to provide a state (x,y)? > ").upper()
        if(sim_or_reach_state == 'SIM'):
            sim_or_state = False
            start_simulation_sim_time(no_of_jobs_server_1, no_of_jobs_server_2, arrival_rate, job_distribution, sim_time)
        elif(sim_or_reach_state == 'STATE'):
            given_x             = input("What is the desired state for server 1? > ")
            given_y             = input("What is the desired state for server 2? > ")
            sim_or_state = False
            start_simulation_state(no_of_jobs_server_1, no_of_jobs_server_2, arrival_rate, job_distribution, given_x, given_y, sim_time)
            # Allow user to pick if he wants to print the stats to file or something (create function for that aswell, to get the name)
        else:
            print("Sorry, I did not understand the input, please pick SIM or STATE")
def start_screen_1():
    clear()
    print("You picked reach box.")
    print("Here we have 2 servers, 1 dispatcher. JSQ policy, expo service rate of 1 for each server, and varying arrival from 0.1 to 1.9")
    given_n = input("What n would you like (e.g. 4) for the starting state of (n+1, n) > ")
    sim_timeout = input("What is the timeout? (each simulation will run for max this amount of time before timing out) > ")
    name_of_file = input("What would you like the names of the files to be ? e.g. name_of_file_[arrival_rate].txt > ")
    print("Starting simulation, this may take a while...")
    start_sim_less_than(given_n, sim_timeout, name_of_file)

# A simulation, starting from a given state and running until the simulation time is over.
# Uses 2 servers and 1 dispatcher with JSQ
def start_simulation_sim_time(no_of_jobs_server_1, no_of_jobs_server_2, arrival_rate, job_distribution, sim_time):
    list_of_servers = []
    for _ in range(0,2): # Create 2 servers
        scheduler_i = FIFO()
        job_size_i = Expo(job_distribution)
        server_i = Server(job_size_i, scheduler_i)
        list_of_servers.append(server_i)
    policy_i = ShortestQueue() #Join shortest queue policy
    dispatcher = Dispatcher(policy_i, list_of_servers) #Create a dispatcher with JSQ policy
    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(float(arrival_rate))

    #For each job in server 1 we:
    #Create a job with arrival at time 0, then increase # of jobs in the server.
    #We get time the job enters service, either immediately or after the total processing done.
    #Set the enter service and service time needed.
    #Next calculate departure time and set it, then we can schedule the departure.
    server_1_processing_time = 0
    #Forloops used to create a given # of jobs before starting sim
    for job in range(0, int(no_of_jobs_server_1)):
        job = Job(0) #All arrive at time 0
        list_of_servers[0]._total_jobs +=1
        enter_service = max(list_of_servers[0]._total_processing_time, 0) #Takes processing time (time when server is idle) and the time of arrival. Max of those is enter service for this job
        job.set_enter_service(enter_service) #Setting the enter service, first is 0, next is 0+service_1, next is 0+service_1 + service_2.. ...
        job.set_service(list_of_servers[0].get_service_time()) #Generates service time AND increases processing time for server
        departure_time = job._enter_service + job._service_time # Enter service will be correct because of processing time of server bookkeeping
        job.set_departure(departure_time) #Set the departure time as enter service+service time. (Its a timeperiod on the timeline)
        world.schedule_event(list_of_servers[0].departure, job._departure_time, [job, world]) #Schedule this departure to the world queue
    for job in range(0, int(no_of_jobs_server_2)):
        job = Job(0)
        list_of_servers[1]._total_jobs +=1
        enter_service = max(list_of_servers[1]._total_processing_time, 0)
        job.set_enter_service(enter_service)
        job.set_service(list_of_servers[1].get_service_time())
        departure_time = job._enter_service + job._service_time
        job.set_departure(departure_time)
        world.schedule_event(list_of_servers[1].departure, job._departure_time, [job, world])
    
    initial_arrival = random.expovariate(p_arrivals._rate)
    params = [dispatcher, world]
    world.schedule_event(p_arrivals.generate_arrival, initial_arrival, params) #Schedule first arrival to start chain

    world.number_of_arr_dep = 0 #resetting the number of events before we start
    # Now we need to schedule the initial arrivals to start the chain of events.
    for x in range(1, 11):
        # Now that each dispatcher has an arrival, we can start looping through events
        while world.next_event() <= float(sim_time)*(x*0.1): # while the virtual time of next event is less than our simulation time..
            world.process_event() # We take the event and process it (running the function(s))
        print("{}%".format(x*10))
    #for loop to step between while loops (every 10%)while world.next

    total_no_jobs = world._stats.number_of_jobs
    print(total_no_jobs)
    world._stats.print_stats()

def start_simulation_less_than_n(no_of_jobs_server_1, no_of_jobs_server_2, arrival_rate, job_distribution, sim_time):
    list_of_servers = []
    global jobs_ran
    global final_data
    stopping_n = no_of_jobs_server_2 
    for _ in range(0,2): # Create 2 servers
        scheduler_i = FIFO()
        job_size_i = Expo(job_distribution)
        server_i = Server(job_size_i, scheduler_i)
        list_of_servers.append(server_i)
    # Create dispatcher
    policy_i = ShortestQueue() #Join shortest queue policy
    dispatcher = Dispatcher(policy_i, list_of_servers) #Create a dispatcher with JSQ policy

    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(float(arrival_rate))
    arrival = 0

    #For each job in server 1 we:
    #Create a job with arrival at time 0, then increase # of jobs in the server.
    #We get time the job enters service, either immediately or after the total processing done.
    #Set the enter service and service time needed.
    #Next calculate departure time and set it, then we can schedule the departure.
    server_1_processing_time = 0
    for job in range(0, int(no_of_jobs_server_1)):
        job = Job(0) #All arrive at time 0
        list_of_servers[0]._total_jobs +=1
        enter_service = max(list_of_servers[0]._total_processing_time, 0) #Takes processing time (time when server is idle) and the time of arrival. Max of those is enter service for this job
        job.set_enter_service(enter_service) #Setting the enter service, first is 0, next is 0+service_1, next is 0+service_1 + service_2.. ...
        job.set_service(list_of_servers[0].get_service_time()) #Generates service time AND increases processing time for server
        departure_time = job._enter_service + job._service_time # Enter service will be correct because of processing time of server bookkeeping
        job.set_departure(departure_time) #Set the departure time as enter service+service time. (Its a timeperiod on the timeline)
        world.schedule_event(list_of_servers[0].departure, job._departure_time, [job, world]) #Schedule this departure to the world queue
    for job in range(0, int(no_of_jobs_server_2)):
        job = Job(0)
        list_of_servers[1]._total_jobs +=1
        enter_service = max(list_of_servers[1]._total_processing_time, 0)
        job.set_enter_service(enter_service)
        job.set_service(list_of_servers[1].get_service_time())
        departure_time = job._enter_service + job._service_time
        job.set_departure(departure_time)
        world.schedule_event(list_of_servers[1].departure, job._departure_time, [job, world])
    
    initial_arrival = random.expovariate(p_arrivals._rate)
    params = [dispatcher, world]
    world.schedule_event(p_arrivals.generate_arrival, initial_arrival, params) #Schedule first arrival to start chain

    last_event = 0
    world.number_of_arr_dep = 0 #resetting the number of events before we start
    # Now we need to schedule the initial arrivals to start the chain of events.
    # Now that each dispatcher has an arrival, we can start looping through events
    while world.next_event() <= float(sim_time): # while the virtual time of next event is less than our simulation time..
        if(list_of_servers[0]._total_jobs<=stopping_n and list_of_servers[1]._total_jobs <= stopping_n):
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
    
def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

def start_sim_less_than(given_n, sim_timeout, name_of_file):

    lst = drange(0.1, 2, 0.1)
    y = 0
    global jobs_ran
    lst_jobs_through_system = [math.pow(10,5), math.pow(10,5), math.pow(10,5), math.pow(10,5), math.pow(10,5), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,6), math.pow(10,7), math.pow(10,7), math.pow(10,7)]
    for x in lst: #from 0.1 to 1.9 with 0.1 step-wise
        jobs_ran = 0
        final_data.clear()
        while jobs_ran<lst_jobs_through_system[y]:
            start_simulation_less_than_n(int(given_n)+1,int(given_n),x,1,int(sim_timeout))
        y += 1
        with open(name_of_file+"_"+str(round(x,1))+'.txt', 'a') as myfile:
            for line in final_data:
                data = "{0},{1},{2:<8.5f},{3}".format(line[0], line[1], line[2], line[3])
                myfile.write(data+"\n")
        print("Finished with step: {}".format(round(x,1)))

def start_simulation_state(no_of_jobs_server_1, no_of_jobs_server_2, arrival_rate, job_distribution, given_x, given_y, sim_time):
    list_of_servers = []
    for _ in range(0,2): # Create 2 servers
        scheduler_i = FIFO()
        job_size_i = Expo(job_distribution)
        server_i = Server(job_size_i, scheduler_i)
        list_of_servers.append(server_i)
    # Create dispatcher
    policy_i = ShortestQueue() #Join shortest queue policy
    dispatcher = Dispatcher(policy_i, list_of_servers) #Create a dispatcher with JSQ policy

    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(float(arrival_rate))
    arrival = 0

    
    def set_up_servers():
        nonlocal list_of_servers, world
        for job in range(0, int(no_of_jobs_server_1)):
            job = Job(0) #All arrive at time 0
            list_of_servers[0]._total_jobs +=1
            enter_service = max(list_of_servers[0]._total_processing_time, 0) #Takes processing time (time when server is idle) and the time of arrival. Max of those is enter service for this job
            job.set_enter_service(enter_service) #Setting the enter service, first is 0, next is 0+service_1, next is 0+service_1 + service_2.. ...
            job.set_service(list_of_servers[0].get_service_time()) #Generates service time AND increases processing time for server
            departure_time = job._enter_service + job._service_time # Enter service will be correct because of processing time of server bookkeeping
            job.set_departure(departure_time) #Set the departure time as enter service+service time. (Its a timeperiod on the timeline)
            world.schedule_event(list_of_servers[0].departure, job._departure_time, [job, world]) #Schedule this departure to the world queue
        # Now we have some jobs already in the server(s) before we start the main loop of adding arrivals e.t.c.
        for job in range(0, int(no_of_jobs_server_2)):
            job = Job(0)
            list_of_servers[1]._total_jobs +=1
            enter_service = max(list_of_servers[1]._total_processing_time, 0)
            job.set_enter_service(enter_service)
            job.set_service(list_of_servers[1].get_service_time())
            departure_time = job._enter_service + job._service_time
            job.set_departure(departure_time)
            world.schedule_event(list_of_servers[1].departure, job._departure_time, [job, world])
        #cost function is basically sojourn time in these cases.    

    #### IMPORTANT
    # Need here to make a check to see if we're out of bounds before each process_event
    # If we're out of bounds we 'stop' and save the stats.
    # Then reset the 'world' and run again, until the sim_time is over. 
    # May be best to do a sub-routine to 'reset' the world (can be used for both simulation processes)
    
    def reset_world(first_arrival):
        nonlocal list_of_servers, dispatcher, statistics, world # if we want to modify variable from closure, must place as nonlocal
        list_of_servers.clear() #clear the 2 servers
        for _ in range(0,2): # Create 2 servers
            scheduler_i = FIFO()
            job_size_i = Expo(job_distribution) # use job_distr from closure
            server_i = Server(job_size_i, scheduler_i) # create a new server to place in list
            list_of_servers.append(server_i)
        dispatcher = Dispatcher(policy_i, list_of_servers) # resetting the dispatcher with new servers
        statistics = Statistics()
        world = Global(statistics)
        set_up_servers()
        params = [dispatcher, world]
        world.schedule_event(p_arrivals.generate_arrival, first_arrival, params) #Schedule first arrival to start chain
        #Now we have created two new servers, reset them and created a dispatcher with the new servers
        #Then we reset the world(nonlocal) and statistics to get a clean slate
        #Then we called function to set the initial jobs in the servers again (not same jobs!)

    reset_world(0) # Call function to setup our world

    # Now we need to schedule the initial arrivals to start the chain of events.
    for x in range(1, 11):
        # Now that each dispatcher has an arrival, we can start looping through events
        while world.next_event() <= float(sim_time)*(x*0.1): # while the virtual time of next event is less than our simulation time..
            if list_of_servers[0]._total_jobs > int(given_x) or list_of_servers[1]._total_jobs > int(given_y):
                next_arrival_new_world = world.next_event() #Get the time for the first event for new world
                #reset the world here (e.g. clear all stats and world queue, then reset jobs in servers and 'restart')
                print('resetting world')
                world._stats.write_to_file_intermediate_stats('given_end_of_'+given_x+'_and_'+given_y)
                reset_world(next_arrival_new_world) # This function should reset statistics, world event queue, and server states
                #also remember to log the stats before reset.
            world.process_event() # We take the event and process it (running the function(s))
        print("{}%".format(x*10))
    #for loop to step between while loops (every 10%)while world.next

    total_no_jobs = world._stats.number_of_jobs
    print(total_no_jobs)
    world._stats.print_stats()
    #When done, we can print out stats?


start_screen()