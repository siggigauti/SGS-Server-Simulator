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


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.random_policy = policies.RND()
        self.shortest_queue_policy = policies.ShortestQueue()
        self.servers = simutil.init_servers(5, [1, 1, 1, 1, 1], [2, 2, 2, 2, 2])

    def test_has_make_decision(self):
        self.assertIn("make_decision", dir(self.random_policy))
        self.assertIn("make_decision", dir(self.shortest_queue_policy))

    def test_makes_a_decision(self):
        self.assertIn(self.random_policy.make_decision(self.servers, Job(0, 0.5)), range(0, 5))
        self.assertIn(self.shortest_queue_policy.make_decision(self.servers, Job(0, 0.5)), range(0, 5))


if __name__ == '__main__':
    unittest.main()
