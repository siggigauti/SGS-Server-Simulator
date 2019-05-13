from simulator.schedulers import FIFO, PS
from simulator.dispatcher import Dispatcher
from simulator.job import Job
from simulator.server import Server
from simulator.policies import RND, ShortestQueue, SED, Qlearning, NO_Matrix
import os


def clear():
    # Checks if windows or other.
    os.system("cls" if os.name == "nt" else "clear")

# returns a list of servers with given schedulers and distributions.


def init_servers(no_of_servers, server_schedulers, server_service_rates):
    list_of_servers = []
    for i in range(int(no_of_servers)):
        scheduler_i = FIFO() if server_schedulers[i] == 1 else PS()
        server_i = Server(server_service_rates[i], scheduler_i)
        list_of_servers.append(server_i)
    return list_of_servers

# returns a list of dispatchers with given policy and access to given servers


def init_dispatchers(no_of_dispatchers, dispatcher_policy, list_of_servers, qlearn, policyseed=None, td_matrix_and_backup=None):
    list_of_dispatchers = []
    for i in range(int(no_of_dispatchers)):
        if dispatcher_policy[i] == 1:
            policy_i = RND(policyseed)
        elif dispatcher_policy[i] == 2:
            policy_i = ShortestQueue(policyseed)
        elif dispatcher_policy[i] == 3:
            policy_i = Qlearning(qlearn[0], qlearn[1], qlearn[2], qlearn[3], list_of_servers[i], policyseed)
        elif dispatcher_policy[i] == 4:
            policy_i = SED(policyseed)
        elif dispatcher_policy[i] == 5:
            policy_i = NO_Matrix(td_matrix_and_backup[0], policyseed=policyseed, backup_policy=td_matrix_and_backup[1])
        dispatcher_i = Dispatcher(policy_i, list_of_servers[i])
        list_of_dispatchers.append(dispatcher_i)
    return list_of_dispatchers

# Takes the world, dispatchers and poisson arrival class to create initial jobs


def init_first_jobs(world, list_of_dispatchers, p_arrivals):
    for d in list_of_dispatchers:
        p_arrivals.first_arrival([d, world])

# Function to initialize n jobs in given server


def init_server_to_state(no_of_jobs, server, scheduler_type, world):
    for _ in range(0, int(no_of_jobs)):
        job = Job(0)  # All arrive at time 0
        server._total_jobs += 1
        enter_service = server._scheduler.enter_service(0, server._total_processing_time)  # Takes processing time (time when server is idle) and the time of arrival. Max of those is enter service for this job
        job.set_enter_service(enter_service)  # Setting the enter service, first is 0, next is 0+service_1, next is 0+service_1 + service_2.. ...
        job.set_service(server.get_service_time())  # Generates service time AND increases processing time for server
        if scheduler_type == 1:  # We're using FIFO
            departure_time = job._enter_service + job._service_time  # Enter service will be correct because of processing time of server bookkeeping
            job.set_departure(departure_time)  # Set the departure time as enter service+service time. (Its a timeperiod on the timeline)
            world.schedule_event(server.departure, job._departure_time, [job, world])  # Schedule this departure to the world queue

# Function to save stats to file


def save_stats(world):
    save_stats = input("Do you want to save these stats to file Y/N?").upper()
    if save_stats == 'Y':
        file_name = input("What name for the file? > ")
        print("Thank you, your stats will be saved in the Simulation_results directory.")
        world._stats.write_to_file_stats(file_name)


def print_step_matrix(dispatcher):
    print('The Q: ' + str(dispatcher._policy.Q))
    v = dispatcher._policy.v
    v2 = dispatcher._policy.v2
    print('mean cost rate r: ' + str(dispatcher._policy.r))
    print('The v:')
    i = 0
    for key in v:
        i += 1
        print(str(key) + ': ' + str(v[key]) + '  ')
        if not i % 5:
            print('\n')
    print('The v2:')
    i = 0
    for key in v2:
        i += 1
        print(str(key) + ': ' + str(v2[key]) + '\n')
        if not i % 5:
            print('\n')
