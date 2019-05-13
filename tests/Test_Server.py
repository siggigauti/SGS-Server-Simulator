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


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.job = Job(0, 0.5)
        self.stats = stats.Statistics()
        self.world = global_state.Global(self.stats)
        self.service = Expo(1)
        self.scheduler = schedulers.FIFO()
        self.server = Server(self.service, self.scheduler)
        self.policy = policies.RND()

    def test_departure(self):
        self.server._total_jobs = 1
        self.server.departure(1, [self.job, self.world, self.policy])
        self.assertEqual(self.server._total_jobs, 0)


if __name__ == '__main__':
    unittest.main()
