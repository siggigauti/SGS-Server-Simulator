import unittest
import math
import sys
sys.path.append('../')
import simulator.arrivals as arrivals
import simulator.global_state as global_state
import simulator.policies as policies
from simulator.job import Job
from simulator.job_size import Expo
import simulator.schedulers as schedulers
from simulator.server import Server
import statistics_and_graphs.stats as stats
import utility.sim_utility as simutil
import gc


class GlobalTests(unittest.TestCase):
    def setUp(self):
        self.stats = stats.Statistics()
        self.world = global_state.Global(self.stats)
        job_size_rate = 1
        job_sizes = Expo(job_size_rate)
        arr_seed = 100
        self.p_arrivals = arrivals.PoissonArrival(2, job_sizes, arr_seed)
        self.list_of_servers = simutil.init_servers(1, [1], [2])
        self.policy_i = policies.ShortestQueue()
        self.d = simutil.init_dispatchers(1, [2], [self.servers], [], 150)


if __name__ == '__main__':
    unittest.main()
