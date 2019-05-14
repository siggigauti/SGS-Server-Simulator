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
        self.job_sizes = Expo(job_size_rate)
        arr_seed = 100
        self.p_arrivals = arrivals.PoissonArrival(2, self.job_sizes, arr_seed)
        self.list_of_servers = simutil.init_servers(1, [1], [2])
        self.policy_i = policies.ShortestQueue()
        self.d = simutil.init_dispatchers(1, [2], [self.list_of_servers], [], 150)

    def test_schedule_valid_event(self):
        self.world.schedule_event(self.p_arrivals.generate_arrival, 1, [self.d[0], self.world])
        next_event = self.world.eventQueue[0]
        self.assertEqual(next_event[0], 1)

    def test_schedule_invalid_event(self):
        self.assertRaises(ValueError, self.world.schedule_event, self.p_arrivals.generate_arrival, -1, [self.d[0], self.world])

    def test_process_event(self):
        file_data_arrival = arrivals.PoissonArrival(2, self.job_sizes, arr_seed=924, file=[(0.28041127864778986, 1.670055588109133)])
        self.world.schedule_event(file_data_arrival.generate_arrival, 1, [self.d[0], self.world])  # Schedule an event
        self.world.process_event()  # Process the event
        self.assertEqual(file_data_arrival._last_job._arrival_time, 0.28041127864778986)

    def test_next_event(self):
        self.world.schedule_event(self.p_arrivals.generate_arrival, 51, [self.d[0], self.world])
        next_event = self.world.next_event()
        self.assertEqual(next_event, 51)


if __name__ == '__main__':
    unittest.main()
