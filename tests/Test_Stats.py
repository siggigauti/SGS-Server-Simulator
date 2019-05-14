import unittest
import sys
sys.path.append('../')
from simulator.job import Job
import statistics_and_graphs.stats as stats


class StatsTests(unittest.TestCase):
    def setUp(self):
        self.stats = stats.Statistics()

    def test_add_job(self):
        self.stats.add_job(Job(0.28041127864778986, 1.670055588109133))
        # Not finished, need to test that each variable got incremented
        self.assertEqual(self.stats.job_arrival_times[0], 0.28041127864778986)
        self.assertEqual(self.stats.job_sizes[0], 1.670055588109133)


if __name__ == '__main__':
    unittest.main()
