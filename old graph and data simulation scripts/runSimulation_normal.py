#Script to start running a simulation.
import os
import random
from server import Server
from job import Job
from dispatcher import Dispatcher
from arrivals import PoissonArrival
from global_state import Global
from stats import Statistics
from policies import RND, ShortestQueue
from job_size import Expo
from schedulers import FIFO, PS

#A function to clear the screen
def clear():
    #Checks if windows or other.
    os.system("cls" if os.name == "nt" else "clear")

def start_screen():
    clear()
    print("Welcome to trix-simulation #BETA#")
    no_of_servers       = input("How many servers > ")
    server_scheduling   = input("What scheduling algorithm? (1 for FIFO, 2 for PS) > ")
    no_of_dispatchers   = input("How many dispatchers > ")
    dispatcher_policy   = input("What dispatcher policy (1 for RND, 2 for JSQ) > ").upper()
    arrival_rate        = input("What arrival rate would you like? > ")
    job_distribution    = input("What job distribution (only expo supported, provide service rate)? > ")
    sim_time            = input("How long do you want the simulation to be? > ")

    start_simulation(no_of_servers, server_scheduling, no_of_dispatchers, dispatcher_policy, arrival_rate, job_distribution, sim_time)

def start_simulation(no_of_servers, server_scheduler, no_of_dispatchers, dispatcher_policy, arrival_rate, job_distribution, sim_time):
    list_of_servers = []
    list_of_dispatchers = []
    for _ in range(0, int(no_of_servers)):
        scheduler_i = FIFO() if server_scheduler == 1 else PS()
        job_size_i = Expo(job_distribution)
        server_i = Server(job_size_i, scheduler_i)
        list_of_servers.append(server_i)
    for _ in range(0, int(no_of_dispatchers)):
        policy_i = RND() if dispatcher_policy == 1 else ShortestQueue()
        dispatcher_i = Dispatcher(policy_i, list_of_servers)
        list_of_dispatchers.append(dispatcher_i)

    statistics = Statistics()
    world = Global(statistics)
    p_arrivals = PoissonArrival(float(arrival_rate)/len(list_of_dispatchers))

    # Loop to generate first arrivals for each dispatcher
    for d in list_of_dispatchers:
        arrival = random.expovariate(p_arrivals._rate)
        params = [d, world]
        world.schedule_event(p_arrivals.generate_arrival, arrival, params) # Schedule the first arrivals for each dispatcher
    
    # Now that each dispatcher has an arrival, we can start looping through events
    for x in range(1, 101):
        # Now that each dispatcher has an arrival, we can start looping through events
        while world.next_event() <= float(sim_time)*(x*0.01): # while the virtual time of next event is less than our simulation time..
            world.process_event() # We take the event and process it (running the function(s))
        world._stats.write_to_file_jobs()
        print("{}%".format(x))
    #for loop to step between while loops (every 10%)while world.next

    total_no_jobs = world._stats.number_of_jobs
    print(total_no_jobs)
    world._stats.print_stats()
    ## Should add an interactive stage here to see if user wants to save data
    save_stats          = input("Do you want to save these stats to file Y/N?").upper()
    if save_stats == 'Y':
        file_name        = input("What name for the file? > ")
        print("Thank you, your stats will be saved in the Simulation_results directory.")
    world._stats.write_to_file_stats(file_name)
start_screen()