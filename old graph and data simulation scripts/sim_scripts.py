import os
import random
import math
import sys
sys.path.append("..")  # Adds higher directory to python modules path.
from simulator.server import Server
from simulator.job import Job
from simulator.dispatcher import Dispatcher
from simulator.arrivals import PoissonArrival
from simulator.global_state import Global
from statistics_and_graphs.stats import Statistics
from simulator.policies import RND, ShortestQueue, SED, Qlearning
from simulator.job_size import Expo
from simulator.schedulers import FIFO, PS
import utility.sim_utility as simutil
from statistics_and_graphs.auto_graphs import AutoGraphs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import threading
import ast
import time
from scipy.interpolate import spline
import threading
import multiprocessing
import matplotlib.colors as cols


def plotting_MSE():
    all_data = []
    for i in range(0, 20):
        with open('../data_results/TD_learn_server_utilization/2Mjobs_TD_alpha_decay_rho_' + str(i) + '.txt', 'r') as f:
            data = [float(i[8:]) for i in f.read().splitlines()[:-1] if i != '']
        all_data.append(data)
    # All data is of form:
    # [[       ]
    #  [       ]
    #  .........
    #  [       ]]
    #####
    # Where each row is a full simulation (20 of them)
    # each row: state{s1,s2} its the value at that state
    #[ {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4}        for the 5% mark
    #  {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4}        10%
    #  ....                                                       15%, 20%, ...
    #  {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4} ]      100%

    RND_value_matrix = []
    for i in range(0, 5):
        for j in range(0, 5):
            RND_value_matrix.append((i * (i + 1) + j * (j + 1)))
    MSE = 0
    mean_simulation = [0.0] * 500
    for sim in all_data:  # There are 20 simulations
        mean_simulation = [sum(i) for i in zip(sim, mean_simulation)]
    mean_simulation = [i / 20 for i in mean_simulation]
    percent_data = [mean_simulation[x:x + 25] for x in range(0, len(mean_simulation), 25)]

    plt_data = []
    for prc_data in percent_data:
        plt_data.append((sum(math.pow(o[0] - o[1], 2) for o in zip(prc_data, RND_value_matrix))) / len(RND_value_matrix))

    all_data2 = []
    for i in range(0, 20):
        with open('../data_results/TDlearn/1Mjobs_TD_alpha_decay_test_RND_' + str(i) + '.txt', 'r') as f:
            data = [float(i[8:]) for i in f.read().splitlines()[:-1] if i != '']
        all_data2.append(data)
    # All data is of form:
    # [[       ]
    #  [       ]
    #  .........
    #  [       ]]
    #####
    # Where each row is a full simulation (20 of them)
    # each row: state{s1,s2} its the value at that state
    #[ {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4}        for the 5% mark
    #  {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4}        10%
    #  ....                                                       15%, 20%, ...
    #  {0,0}, ..,{0,4},{1,0}, ..,{1,4},...,{4,0}, ..,{4,4} ]      100%

    MSE = 0
    mean_simulation2 = [0.0] * 500
    for sim in all_data2:  # There are 20 simulations
        mean_simulation2 = [sum(i) for i in zip(sim, mean_simulation2)]
    mean_simulation2 = [i / 20 for i in mean_simulation2]
    percent_data2 = [mean_simulation2[x:x + 25] for x in range(0, len(mean_simulation2), 25)]

    plt_data2 = []
    for prc_data in percent_data2:
        plt_data2.append((sum(math.pow(o[0] - o[1], 2) for o in zip(prc_data, RND_value_matrix))) / len(RND_value_matrix))

    # plt_data = [math.log2(i) for i in plt_data]
    print(plt_data)
    print(plt_data2)
    x = [i for i in range(5, 101, 5)]
    x_sm = np.array(x)
    y_sm = np.array(plt_data)
    x_smooth = np.linspace(x_sm.min(), x_sm.max(), 200)
    y_smooth = spline(x, plt_data, x_smooth)
    y_sm = np.array(plt_data2)
    y_smooth2 = spline(x, plt_data2, x_smooth)
    plt.plot(x_smooth, y_smooth, 'b-', label='alpha = 0.1')
    plt.plot(x_smooth, y_smooth2, 'r-', label='alpha decay')
    plt.ylim([0, 35])
    plt.xlabel('Jobs completed')
    plt.ylabel('Mean squared error')
    plt.xticks([20, 40, 60, 80, 100], ['200K', '400K', '600K', '800K', '1M'])
    plt.show()


def q_testing_id(id):
    sim_time = 2000000
    list_of_servers = simutil.init_servers(2, [1, 1], [3, 1])  # 2 servers using FIFO and mui = 3, and 1
    list_of_dispatchers = simutil.init_dispatchers(1, [3], [list_of_servers], [[4, 4], [], [], sim_time])  # 1 dispatcher, Qlearn, 5x5 box, nothing excluded.
    statistics = Statistics()
    world = Global(statistics)
    job_sizes = Expo(2)  # Lambda = 2,  rho will be lambda / (3+1) = 0.5
    p_arrivals = PoissonArrival(1, job_sizes)  # Poisson arrivals with 1 arrival rate.
    simutil.init_first_jobs(world, list_of_dispatchers, p_arrivals)
    # Main loop

    for x in range(1, 101):
        while world.next_event() <= float(sim_time) * (x * 0.01):  # while the virtual time of next event is less than our simulation time..
            world.process_event()  # We take the event and process it (running the function(s))
        # world._stats.write_to_file_jobs()
        print("thread id: {}, finised {}%".format(id, x))
        if(x % 5 == 0):
            v2 = list_of_dispatchers[0]._policy.v2
            with open('../data_results/TD_learn_server_utilization/2Mjobs_TD_alpha_decay_rho_' + str(id) + '.txt', 'a') as f:
                for key in v2:
                    f.write(str(key) + ': ' + str(v2[key]) + '\n')
                f.write('\n')


def td_learn_server_utilization(rho, round_nr):
    sim_time = 5000000
    list_of_servers = simutil.init_servers(2, [1, 1], [3, 1])  # 2 servers using FIFO and mui = 3, and 1
    list_of_dispatchers = simutil.init_dispatchers(1, [3], [list_of_servers], [[12, 4], [], [], sim_time])  # 1 dispatcher, Qlearn, 5x5 box, nothing excluded.
    statistics = Statistics()
    world = Global(statistics)
    # arrival_rate = 2  # get the arrival rate by using given rho
    job_sizes = Expo(1)  # Lambda = 2,  rho will be lambda / (3+1) = 0.5
    p_arrivals = PoissonArrival(3.92, job_sizes)  # Poisson arrivals with 1 arrival rate.
    simutil.init_first_jobs(world, list_of_dispatchers, p_arrivals)
    # Main loop

    for x in range(1, 101):
        while world.next_event() <= float(sim_time) * (x * 0.01):  # while the virtual time of next event is less than our simulation time..
            world.process_event()  # We take the event and process it (running the function(s))
        # world._stats.write_to_file_jobs()
        print("round: {}, rho: {}, finised {}%".format(round_nr, rho, x))

    v2 = list_of_dispatchers[0]._policy.v2
    with open('../data_results/TD_learn_server_utilization/500kjobs_SED_rho_' + str(rho) + '-3.txt', 'a') as f:
        for key in v2:
            f.write(str(key) + ': ' + str(v2[key]) + '\n')
        f.write('\n')


class myThread(threading.Thread):
    def __init__(self, threadID, rho, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.rho = rho
        self.counter = counter

    def run(self):
        for i in range(self.counter):
            td_learn_server_utilization(self.rho, i)


def plot_action_from_matrix(filename):
    matrix = {}
    plottin_matrix = np.empty([0, 4])
    lines = None
    with open('../' + filename, 'r') as f:
        lines = f.read().splitlines()[:]
    lines = [(i.split(': ')) for i in lines]
    for line in lines:
        print(line)
        matrix[line[0]] = float(line[1])
    # plotting matrix, 1 entry for picking server 1, 0 entry for picking server 0
    row_counter = 0
    row = []
    for key, value in matrix.items():

        if ast.literal_eval(key)[0] == 12:
            continue
        if ast.literal_eval(key)[1] == 4:
            continue
        # print('key: {}, value: {}'.format(key, value))
        values = []
        for j in range(2):  # Step in every direction
            dx = ast.literal_eval(key)  # copy state x

            dx[j] += 1   # dx = new state in direction j
            # print('State: {}, value: {}'.format(dx, matrix[str(dx)]))
            values.append(matrix[str(dx)])  # Add the value function for that step
        k = values.index(min(values))  # returns 0 or 1. Ties in random
        row.append(k)
        # print('Given states chose: {}'.format(k))
        row_counter += 1
        if row_counter == 4:
            print(row)
            plottin_matrix = np.vstack((plottin_matrix, row))
            row = []  # empty the row
            row_counter = 0  # empty counter

    print(plottin_matrix)
    # plottin_matrix = np.rot90(plottin_matrix,1)

    cdict1 = {'red': ((0.0, 0.0, 0.0),
                      (0.5, 0.0, 0.1),
                      (1.0, 1.0, 1.0)),

              'green': ((0.0, 0.0, 0.0),
                        (1.0, 0.0, 0.0)),

              'blue': ((0.0, 0.0, 1.0),
                       (0.5, 0.1, 0.0),
                       (1.0, 0.0, 0.0))
              }
    blue_red1 = cols.LinearSegmentedColormap('BlueRed1', cdict1)

    plt.imshow(plottin_matrix.T, cmap=blue_red1, origin='lower')
    ax = plt.gca()
    ax.set_xticks(np.arange(-.5, 12, 1))
    ax.set_yticks(np.arange(-.5, 4, 1))
    ax.set_xticklabels(np.arange(0, 12, 1))
    ax.set_yticklabels(np.arange(0, 4, 1))
    plt.grid(which='major', axis='both', linestyle='-')
    """
    plt.plot([0.5, 0.5], [-0.5, 0.5], c='black', linewidth=3)
    plt.plot([0.5, 3.5], [0.5, 0.5], c='black', linewidth=3)
    plt.plot([3.5, 3.5], [0.5, 1.5], c='black', linewidth=3)
    plt.plot([3.5, 5.5], [1.5, 1.5], c='black', linewidth=3)
    plt.plot([5.5, 5.5], [1.5, 2.5], c='black', linewidth=3)
    plt.plot([5.5, 8.5], [2.5, 2.5], c='black', linewidth=3)
    plt.plot([8.5, 8.5], [2.5, 3.5], c='black', linewidth=3)
    plt.title('Offered load = 0.75')
    plt.xlabel('Number of jobs in server 1')
    plt.ylabel('Number of jobs in server 2')
    plt.setp(ax.xaxis.get_majorticklabels(), ha="left")
    dx = 10 / 72.
    dy = 0 / 72.
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    plt.setp(ax.yaxis.get_majorticklabels(), ha="left")
    dx = -5 / 72.
    dy = 15 / 72.
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)
    for label in ax.yaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    """
    plt.show()


def plot_SED1_figure():

    plottin_matrix = np.empty([0, 4])
    rows = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,1,0,0],[1,1,0,0],[1,1,0,0],[1,1,1,0],[1,1,1,0],[1,1,1,0]]
    for row in rows:
        plottin_matrix = np.vstack((plottin_matrix, row))

    cdict1 = {'red': ((0.0, 0.0, 0.0),
                      (0.5, 0.0, 0.1),
                      (1.0, 1.0, 1.0)),

              'green': ((0.0, 0.0, 0.0),
                        (1.0, 0.0, 0.0)),

              'blue': ((0.0, 0.0, 1.0),
                       (0.5, 0.1, 0.0),
                       (1.0, 0.0, 0.0))
              }
    blue_red1 = cols.LinearSegmentedColormap('BlueRed1', cdict1)

    plt.imshow(plottin_matrix.T, cmap=blue_red1, origin='lower')
    ax = plt.gca()
    ax.set_xticks(np.arange(-.5, 12, 1))
    ax.set_yticks(np.arange(-.5, 4, 1))
    ax.set_xticklabels(np.arange(0, 12, 1))
    ax.set_yticklabels(np.arange(0, 4, 1))
    plt.grid(which='major', axis='both', linestyle='-')

    plt.plot([2.5, 2.5], [-0.5, 0.5], c='black', linewidth=3)
    plt.plot([2.5, 5.5], [0.5, 0.5], c='black', linewidth=3)
    plt.plot([5.5, 5.5], [0.5, 1.5], c='black', linewidth=3)
    plt.plot([5.5, 8.5], [1.5, 1.5], c='black', linewidth=3)
    plt.plot([8.5, 8.5], [1.5, 2.5], c='black', linewidth=3)
    plt.plot([8.5, 11.5], [2.5, 2.5], c='black', linewidth=3)

    plt.title('SED, tie to server 1')
    plt.xlabel('Number of jobs in server 1')
    plt.ylabel('Number of jobs in server 2')
    plt.setp(ax.xaxis.get_majorticklabels(), ha="left")
    dx = 10 / 72.
    dy = 0 / 72.
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    plt.setp(ax.yaxis.get_majorticklabels(), ha="left")
    dx = -5 / 72.
    dy = 15 / 72.
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)
    for label in ax.yaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    plt.show()


def plot_SED2_figure():

    plottin_matrix = np.empty([0, 4])
    rows = [[0,0,0,0],[0,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,1,0,0],[1,1,0,0],[1,1,0,0],[1,1,1,0],[1,1,1,0],[1,1,1,0],[1,1,1,1]]
    for row in rows:
        plottin_matrix = np.vstack((plottin_matrix, row))

    cdict1 = {'red': ((0.0, 0.0, 0.0),
                      (0.5, 0.0, 0.1),
                      (1.0, 1.0, 1.0)),

              'green': ((0.0, 0.0, 0.0),
                        (1.0, 0.0, 0.0)),

              'blue': ((0.0, 0.0, 1.0),
                       (0.5, 0.1, 0.0),
                       (1.0, 0.0, 0.0))
              }
    blue_red1 = cols.LinearSegmentedColormap('BlueRed1', cdict1)

    plt.imshow(plottin_matrix.T, cmap=blue_red1, origin='lower')
    ax = plt.gca()
    ax.set_xticks(np.arange(-.5, 12, 1))
    ax.set_yticks(np.arange(-.5, 4, 1))
    ax.set_xticklabels(np.arange(0, 12, 1))
    ax.set_yticklabels(np.arange(0, 4, 1))
    plt.grid(which='major', axis='both', linestyle='-')

    plt.plot([1.5, 1.5], [-0.5, 0.5], c='black', linewidth=3)
    plt.plot([1.5, 4.5], [0.5, 0.5], c='black', linewidth=3)
    plt.plot([4.5, 4.5], [0.5, 1.5], c='black', linewidth=3)
    plt.plot([4.5, 7.5], [1.5, 1.5], c='black', linewidth=3)
    plt.plot([7.5, 7.5], [1.5, 2.5], c='black', linewidth=3)
    plt.plot([7.5, 10.5], [2.5, 2.5], c='black', linewidth=3)
    plt.plot([10.5, 10.5], [2.5, 3.5], c='black', linewidth=3)

    plt.title('SED, tie to server 2')
    plt.xlabel('Number of jobs in server 1')
    plt.ylabel('Number of jobs in server 2')
    plt.setp(ax.xaxis.get_majorticklabels(), ha="left")
    dx = 10 / 72.
    dy = 0 / 72.
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    plt.setp(ax.yaxis.get_majorticklabels(), ha="left")
    dx = -5 / 72.
    dy = 15 / 72.
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)
    for label in ax.yaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    plt.show()
if __name__ == '__main__':
    #plot_SED2_figure()
    # plot_action_from_matrix('./data_results/Spring_paper_figures/v2matrix_500k_jobs.txt')
    # plot_action_from_matrix('./data_results/TD_learn_server_utilization/500kjobs_SED_rho_0.75-3.txt')
    #td_learn_server_utilization(0.98, 42)
    """
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=td_learn_server_utilization, args=(0.75, i))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=td_learn_server_utilization, args=(0.98, i))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=td_learn_server_utilization, args=(0.98, i))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
    """
