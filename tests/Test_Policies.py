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
        self.sed_policy = policies.SED()
        self.servers = simutil.init_servers(5, [1, 1, 1, 1, 1], [2, 2, 2, 2, 2])
        self.td_learn_policy = policies.TDlearning([4, 4], [], [], 100, self.servers)

    def test_JSQ_seed(self):
        jsq = policies.ShortestQueue(policyseed=100)
        random_number = jsq._rnd_stream.rand()
        self.assertEqual(random_number, 0.5434049417909654)

    def test_RND_seed(self):
        rnd = policies.RND(policyseed=100)
        random_number = rnd._rnd_stream.rand()
        self.assertEqual(random_number, 0.5434049417909654)

    def test_SED_seed(self):
        sed = policies.SED(policyseed=100)
        random_number = sed._rnd_stream.rand()
        self.assertEqual(random_number, 0.5434049417909654)

    def test_sed_noseed(self):
        sed = policies.SED()
        self.assertNotEqual(sed._rnd_stream, None)

    def test_has_rnd_make_decision(self):
        self.assertIn("make_decision", dir(self.random_policy))

    def test_has_sed_make_decision(self):
        self.assertIn("make_decision", dir(self.sed_policy))

    def test_has_jsq_make_decision(self):
        self.assertIn("make_decision", dir(self.shortest_queue_policy))

    def test_has_tdl_make_decision(self):
        self.assertIn("make_decision", dir(self.td_learn_policy))

    def test_rnd_makes_a_decision(self):
        self.assertIn(self.random_policy.make_decision(self.servers, Job(0, 0.5)), range(0, 5))

    def test_jsq_makes_a_decision(self):
        self.assertIn(self.shortest_queue_policy.make_decision(self.servers, Job(0, 0.5)), range(0, 5))

    def test_jsq_make_decision_choose_server_1(self):
        self.servers[1]._total_jobs = 1
        self.assertEqual(self.shortest_queue_policy.make_decision(self.servers, Job(0.2, 0.4)), 0)

    def test_sed_makes_a_decision(self):
        self.assertIn(self.sed_policy.make_decision(self.servers, Job(0, 0.5)), range(0, 5))

    def test_sed_make_decision_choose_server_1(self):
        self.servers[1]._total_jobs = 1
        self.assertEqual(self.sed_policy.make_decision(self.servers, Job(0.2, 0.4)), 0)

    def test_sed_make_decision_heterogeneous_choose_server_1(self):
        heterogeneous_servers = simutil.init_servers(2, [1, 1], [3, 1])
        heterogeneous_servers[0]._total_jobs = 1  # Job to server 0
        self.assertEqual(heterogeneous_servers[0]._service_rate, 3)
        self.assertEqual(heterogeneous_servers[1]._service_rate, 1)
        self.assertEqual(self.sed_policy.make_decision(heterogeneous_servers, Job(0.2, 0.4)), 0)

    def test_tdl_makes_a_decision(self):
        self.assertIn(self.td_learn_policy.make_decision(self.servers, Job(0.2, 0.5)), range(0, 5))

    def test_tdl_departure(self):
        statistics = stats.Statistics()
        world = global_state.Global(statistics)
        self.td_learn_policy.T = 1
        self.td_learn_policy.x[0] = 1
        self.servers[0]._qenabled = True
        self.servers[0].departure(0.2, [Job(0.1, 0.05), world, self.td_learn_policy])


if __name__ == '__main__':
    unittest.main()
