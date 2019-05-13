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

# To test that a method (with a specific name) exists, we do
# self.assertIn("method_name", dir(instance_of_class))
# Another way:
# hasattr(Class, method) and callable(getattr(Class, method));;; Can use self.__class__ instead of Class


class StatsTests(unittest.TestCase):
    def setUp(self):
        self.stats = stats.Statistics()

    def test_add_job(self):
        self.stats.add_job(Job(0, 0.5))
        # Not finished, need to test that each variable got incremented
        self.assertEqual(self.stats.job_arrival_times[1], 0)
        self.assertEqual(self.stats.job_sizes[0], 0.5)


if __name__ == '__main__':
    unittest.main()
