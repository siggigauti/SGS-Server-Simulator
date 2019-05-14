import unittest
import math
import sys
sys.path.append('../')
import simulator.arrivals as arrivals
import simulator.global_state as global_state
from simulator.job_size import Expo
import statistics_and_graphs.stats as stats
import utility.sim_utility as simutil
import gc


class ArrivalTests(unittest.TestCase):
    def setUp(self):
        job_size_rate = 1
        job_sizes = Expo(job_size_rate)
        seed = 500
        self.arrival = arrivals.PoissonArrival(2, job_sizes, arr_seed=seed)

        self.statistics = stats.Statistics()
        self.world = global_state.Global(self.statistics)
        self.servers = simutil.init_servers(2, [1, 1], [2, 2])  # 2 servers, both using 1 (FIFO) and both run at 2 job units service rate.
        self.dispatcher = simutil.init_dispatchers(1, [1], [self.servers], [], 725)

    def tearDown(self):
        self.arrival = None
        self.statistics = None
        self.world = None
        self.servers = None
        self.dispatcer = None
        del self.statistics
        gc.collect()

    def test_creation(self):
        self.assertEqual(self.arrival._rate, 2)

    def test_generation(self):
        self.arrival.generate_arrival(0, [self.dispatcher[0], self.world])
        self.assertTrue(0 <= self.world.next_event() <= math.inf)

    def test_no_seed_creation(self):
        job_size_rate = 1
        job_sizes = Expo(job_size_rate)
        no_seed_arrival = arrivals.PoissonArrival(2, job_sizes)
        self.assertEqual(no_seed_arrival._rate, 2)

    def test_file_data_creation(self):
        job_size_rate = 1
        job_sizes = Expo(job_size_rate)
        f = open('../test_data/simulation_run_for_tests.txt', 'r')
        data = f.read().splitlines()
        f.close()
        data2 = [tuple(float(x) for x in item.split(',')) for item in data[:-1]]
        file_data_arrival = arrivals.PoissonArrival(2, job_sizes, file=data2)
        self.assertTrue(file_data_arrival._from_file)
        file_data_arrival.first_arrival([self.dispatcher[0], self.world])  # Create an arrival
        self.world.process_event()  # Process the arrival event

        self.assertEqual(file_data_arrival._last_job._size, 1.0984470941530513)
        self.assertEqual(file_data_arrival._last_job._arrival_time, 0.6760705301109414)

    def test_file_data_creation_empty_file(self):
        job_size_rate = 1
        job_sizes = Expo(job_size_rate)
        file_data_arrival = arrivals.PoissonArrival(2, job_sizes, arr_seed=924, file=[])
        self.assertEqual(False, file_data_arrival._from_file)
        file_data_arrival.first_arrival([self.dispatcher[0], self.world])  # Create an arrival
        self.world.process_event()  # Process the arrival event
        self.assertEqual(file_data_arrival._last_job._size, 1.670055588109133)
        self.assertEqual(file_data_arrival._last_job._arrival_time, 0.28041127864778986)

    def test_generate_arrival_index_error(self):
        job_size_rate = 1
        job_sizes = Expo(job_size_rate)
        file_data_arrival = arrivals.PoissonArrival(2, job_sizes, arr_seed=924, file=[(0.28041127864778986, 1.670055588109133)])
        self.assertEqual(True, file_data_arrival._from_file)
        file_data_arrival.first_arrival([self.dispatcher[0], self.world])  # Create an arrival
        self.world.process_event()  # Process the arrival event
        self.world.process_event()  # Process the add job
        self.world.process_event()  # Process the exit system
        self.world.process_event()  # Process the next arrival
        self.assertEqual(file_data_arrival._last_job, None)

    def test_generate_arrival_negative_time(self):
        self.assertRaises(ValueError, self.arrival.generate_arrival, -1, [self.dispatcher[0], self.world])


if __name__ == '__main__':
    unittest.main()
