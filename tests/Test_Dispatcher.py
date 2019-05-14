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
from simulator.dispatcher import Dispatcher
import statistics_and_graphs.stats as stats
import utility.sim_utility as simutil
import gc


class DispatcherTests(unittest.TestCase):
    def setUp(self):
        self.servers = simutil.init_servers(2, [1, 1], [2, 2])  # 2 servers, both using 1 (FIFO) and both run at 2 job units service rate.
        self.dispatchers = simutil.init_dispatchers(1, [1], [self.servers], [])
        self.dispatcher = self.dispatchers[0]

    def test_zero_servers_init(self):
        self.assertRaises(ValueError, Dispatcher, policies.RND(), [])

    def test_init(self):
        self.assertEqual(self.dispatcher._servers[0], self.servers[0])

    def test_make_decision(self):
        statistics = stats.Statistics()
        world = global_state.Global(statistics)
        self.dispatcher.make_decision([Job(0.5, 1), world])
        self.assertEqual(world.eventQueue[0][0], 0.5)


if __name__ == '__main__':
    unittest.main()
