import sys
sys.path.append('../')
from simulator.arrivals import PoissonArrival
from simulator.global_state import Global
from simulator.job_size import Expo
from statistics_and_graphs.stats import Statistics
import utility.sim_utility as simutil
import argparse
from timeit import default_timer as timer
import numpy as np
from simulator.policies import ShortestQueue, SED


# Argument parser
# Optional parameter í server listan sjá: https://stackoverflow.com/questions/36166225/using-the-same-option-multiple-times-in-pythons-argparse
# To handle an optional value, you might try using a simple custom type. In this case, the argument to -i is a single comma-delimited string, with the number of splits limited to 2. You would need to post-process the values to ensure there are at least two values specified.
parser = argparse.ArgumentParser(description='Run a simple TD simulation')
parser.add_argument('-st', '--simtime', type=int, help='Simulation time')
parser.add_argument('-as', '--addserver', nargs=2, action='append', type=float)  # 2 arguments combined to list, e.g. script.py -as 1 2 | is going to add a server with FIFO, and service_rate 2
# parser only supports 1 dispatcher at this time.
parser.add_argument('-ad', '--adddispatcher', nargs='+', type=int)  # what policy is first, rest is optional, dimensionality of qlearn box, exclustion needs separate arg
parser.add_argument('-a', '--arrivalrate', type=float, help='Arrival rate (poisson)')
parser.add_argument('-js', '--jobsize', type=float, help='Job distribution size (e.g. Exponential(1/*size*))')
parser.add_argument('-jd', '--jobdistribution', type=int, help='Job distribution (1=Expo, 2=Weibull)')
parser.add_argument('-arrseed', '--arrivalseed', nargs='?', type=int, help='Seed for arrival process generator')
parser.add_argument('-policyseed', '--policyseed', nargs='?', type=int, help='Seed for the policy random generator')
parser.add_argument('-type', '--type', nargs='?', type=int, help='1 for default run, 2 for longer, e.t.c.')
# TODO go over and add more required arguments
# TODO add argument for random seed
args = parser.parse_args()

# TD-learning simulation test


def TD_testing(st, servers, dispatchers, arrival_rate, job_size_rate, job_distribution, qlearn, arrivals_seed=None, policyseed=None, file_name=None, td_matrix=None):
    sim_time = st
    list_of_servers = simutil.init_servers(len(servers[0]), servers[0], servers[1])  # List of servers for 1 dispatcher
    servers_for_dispatchers = []
    servers_for_dispatchers.append(list_of_servers)
    list_of_dispatchers = simutil.init_dispatchers(dispatchers[0], dispatchers[1], servers_for_dispatchers, qlearn, policyseed, td_matrix_and_backup=[td_matrix,SED(policyseed)])  # 1 dispatcher, Qlearn, 5x5 box, nothing excluded.
    statistics = Statistics()
    world = Global(statistics)
    if job_distribution == 1:
        job_sizes = Expo(job_size_rate)
    if file_name is not None:
        print("file name used")
        f = open(file_name, 'r')
        data = f.read().splitlines()
        sim_time = int(data[-1])
        print(sim_time)
        data2 = [tuple(float(x) for x in item.split(',')) for item in data[:-1]]
        p_arrivals = PoissonArrival(arrival_rate, job_sizes, arrivals_seed, file=data2)  # Poisson arrivals with arrival rate 1.
    else:
        p_arrivals = PoissonArrival(arrival_rate, job_sizes, arrivals_seed)  # Poisson arrivals with arrival rate 1.

    simutil.init_first_jobs(world, list_of_dispatchers, p_arrivals)
    # Main loop
    start = timer()
    for x in range(1, 101):
        while world.next_event() <= float(sim_time) * (x * 0.01):  # while the virtual time of next event is less than our simulation time..
            world.process_event()  # We take the event and process it (running the function(s))
        print("{}%".format(x))
    end = timer()
    print("Total time: {}".format(end - start))
    if dispatchers[1] == 3:
        print('The state counter: ' + str(list_of_dispatchers[0]._policy.state_counter))
    total_no_jobs = world._stats.number_of_jobs
    print(total_no_jobs)
    # simutil.print_step_matrix(list_of_dispatchers[0])
    world._stats.print_stats()
    world._stats.save_run(sim_time)
    simutil.save_stats(world)  # Ask user if he wants to save stats to file


if __name__ == '__main__':
    if args.type is None:
        print('{}, {}, {}, {}, {}'.format(args.simtime, args.addserver, args.adddispatcher, args.arrivalrate, args.arrivalseed))
        servers = list(zip(*args.addserver))
        print(servers)
        dispatchers = [1, [args.adddispatcher[0]]]
        if len(args.adddispatcher) > 1:
            qlearn = [[args.adddispatcher[1], args.adddispatcher[2]], [], [], args.simtime]
        else:
            qlearn = []
        TD_testing(args.simtime, servers, dispatchers, args.arrivalrate, args.jobsize, args.jobdistribution, qlearn, args.arrivalseed, args.policyseed)
    elif args.type == 1:
        TD_testing(100, [(1.0,), (2.0,)], [1, [1]], 1, 1, 1, [], 100, 100, file_name='../data_results/testing_save_jobs.txt')
    elif args.type == 2:
        TD_testing(10000, [(1.0, 1.0), (2.0, 2.0)], [1, [1]], 1, 1, 1, [], 100, 200)
    elif args.type == 3:
        TD_testing(2000000, [(1.0, 1.0), (1.0, 1.0)], [1, [3]], 1.75, 1, 1, [[10, 10], [], [], 2000000], 100, 200)  # TD learn with a 5x5 box 2 servers, nothing excluded
    elif args.type == 4:
        TD_testing(100000, [(1.0, 1.0), (1.0, 1.0)], [1, [1]], 1.75, 1, 1, [], 500, 725)  # 2 servers, mui_n = 1, 1.75 arrival rate, rho = 1.75/2, 1 dispatcher, rnd policy
    elif args.type == 5:
        TD_testing(5000000, [(1.0, 1.0), (1.0, 1.0)], [1, [2]], 1.75, 1, 1, [], 500, 725)  # 2 servers, mui_n = 1, 1.75 arrival rate, rho = 1.75/2, 1 dispatcher, jsq policy
    elif args.type == 6:
        TD_testing(1000000, [(1.0, 1.0), (3.0, 1.0)], [1, [4]], 3.92 , 1, 1, [])  # 2 servers, mui_n = 1, 1.75 arrival rate, rho = 1.75/2, 1 dispatcher, jsq policy
    elif args.type == 7:
        # Using TD learned matrix, rho 0.75
        descision_matrix = np.matrix([[0,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,1,0,0],[1,1,0,0],[1,1,1,0],[1,1,1,0],[1,1,1,0],[1,1,1,1],[1,1,1,1],[1,1,1,1]])
        TD_testing(1000000, [(1.0, 1.0), (3.0, 1.0)], [1, [5]], 3.92, 1, 1, [], td_matrix=descision_matrix)
