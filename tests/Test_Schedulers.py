import unittest
import math
import sys
sys.path.append('../')
import simulator.arrivals as arrivals
import simulator.global_state as global_state
import simulator.schedulers as schedulers
from simulator.job import Job
from simulator.job_size import Expo
import statistics_and_graphs.stats as stats
import utility.sim_utility as simutil
import gc


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.ps = schedulers.PS()
        self.fifo = schedulers.FIFO()

    def test_ps_schedule_1_exit(self):
        jobs_to_exit = self.ps.schedule(Job(0.6, 1), [[0.1, Job(0.2, 0.4)], [0.7, Job(0.9, 0.6)]], 0.2)
        self.assertEqual(len(jobs_to_exit[0]), 1)

    def test_ps_schedule_2_exit(self):
        jobs_to_exit = self.ps.schedule(Job(1, 1), [[0.1, Job(0.2, 0.4)], [0.2, Job(0.4, 0.6)], [0.7, Job(0.6, 1.2)]], 0.2)  # Enough time to exit 2 out of 3 jobs.
        self.assertEqual(len(jobs_to_exit[0]), 2)

    def test_ps_enter_service(self):
        enter = self.ps.enter_service(1.6, 3)
        self.assertEqual(enter, 1.6)

    def test_fifo_enter_service_now(self):
        enter = self.fifo.enter_service(2.2, 1.8)
        self.assertEqual(enter, 2.2)

    def test_fifo_enter_service_next_idle(self):
        enter = self.fifo.enter_service(2.2, 2.8)
        self.assertEqual(enter, 2.8)

    def test_fifo_schedule(self):
        job = Job(1, 1)
        job.set_service(job._size / 1)
        enter_service = self.fifo.enter_service(2, 0)
        job.set_enter_service(enter_service)
        jobs_to_exit = self.fifo.schedule(job, [], 1.5)
        self.assertEqual(jobs_to_exit[0][0]._departure_time, 3)


if __name__ == '__main__':
    unittest.main()
