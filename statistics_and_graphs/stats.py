import os
import errno


class Statistics():
    # A class to collect statistics from jobs e.t.c.
    # Used for graphs and other information analysis#
    number_of_jobs = 0
    total_sojourn_time = 0
    second_pass_sojourn = 0
    total_service_time = 0
    second_pass_service = 0
    total_waiting_time = 0
    second_pass_waiting = 0
    jobs_in_server = 0
    job_arrival_times = []
    job_sizes = []

    def __init__(self, *args, **kwargs):  # pragma: no cover
        pass

    def add_job(self, job):
        self.total_sojourn_time += job._sojourn_time
        self.second_pass_sojourn += (job._sojourn_time * job._sojourn_time)
        self.total_service_time += job._service_time
        self.second_pass_service += (job._service_time * job._service_time)
        self.total_waiting_time += job._waiting_time
        self.second_pass_waiting += (job._waiting_time * job._waiting_time)
        self.job_arrival_times.append(job._arrival_time)
        self.job_sizes.append(job._size)

    def print_stats(self):  # pragma: no cover
        print("Total number of jobs: {}".format(self.number_of_jobs))
        if(self.number_of_jobs > 1):
            sojourn_var = (self.second_pass_sojourn - self.total_sojourn_time * self.total_sojourn_time / self.number_of_jobs) / (self.number_of_jobs - 1)
            service_var = (self.second_pass_service - self.total_service_time * self.total_service_time / self.number_of_jobs) / (self.number_of_jobs - 1)
            waiting_var = (self.second_pass_waiting - self.total_waiting_time * self.total_waiting_time / self.number_of_jobs) / (self.number_of_jobs - 1)
        else:
            sojourn_var = 0
            service_var = 0
            waiting_var = 0
        if(self.number_of_jobs > 0):
            sojourn_mean = self.total_sojourn_time / self.number_of_jobs
            service_mean = self.total_service_time / self.number_of_jobs
            waiting_mean = self.total_waiting_time / self.number_of_jobs
        else:
            sojourn_mean = 0
            service_mean = 0
            waiting_mean = 0
        print("Total accumulative sojourn time      : {0:<8.5f}. Mean sojourn time: {1:<8.5f}. Var: {2:<8.5f}".format(self.total_sojourn_time, sojourn_mean, sojourn_var))
        print("Total accumulative service time      : {0:<8.5f}. Mean service time: {1:<8.5f}. Var: {2:<8.5f}".format(self.total_service_time, service_mean, service_var))
        print("Total accumulative waiting time      : {0:<8.5f}. Mean waiting time: {1:<8.5f}. Var: {2:<8.5f}".format(self.total_waiting_time, waiting_mean, waiting_var))

    def server_job_monitor_add(self):
        self.jobs_in_server += 1

    def server_job_monitor_rem(self):
        self.jobs_in_server -= 1

    def write_to_file_jobs(self):  # pragma: no cover
        with open("server_jobs_over_time.txt", "a") as myfile:
            myfile.write(str(self.jobs_in_server) + "\n")

    def get_mean_sd_sojourn(self):  # pragma: no cover
        if self.number_of_jobs > 1:
            data = "{},{}".format((self.total_sojourn_time / self.number_of_jobs), (self.second_pass_sojourn - self.total_sojourn_time * self.total_sojourn_time / self.number_of_jobs) / (self.number_of_jobs - 1))
        return data

    def create_sim_dir(self):  # pragma: no cover
        try:
            os.makedirs('Simulation_results')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def write_to_file_intermediate_stats(self, file_name):  # pragma: no cover
        self.create_sim_dir()
        if(self.number_of_jobs > 1):
            sojourn_var = (self.second_pass_sojourn - self.total_sojourn_time * self.total_sojourn_time / self.number_of_jobs) / (self.number_of_jobs - 1)
            service_var = (self.second_pass_service - self.total_service_time * self.total_service_time / self.number_of_jobs) / (self.number_of_jobs - 1)
            waiting_var = (self.second_pass_waiting - self.total_waiting_time * self.total_waiting_time / self.number_of_jobs) / (self.number_of_jobs - 1)
        else:
            sojourn_var = 0
            service_var = 0
            waiting_var = 0
        if(self.number_of_jobs > 0):
            sojourn_mean = self.total_sojourn_time / self.number_of_jobs
            service_mean = self.total_service_time / self.number_of_jobs
            waiting_mean = self.total_waiting_time / self.number_of_jobs
        else:
            sojourn_mean = 0
            service_mean = 0
            waiting_mean = 0
        data = """Number of jobs = {0}.
        Total accumulative sojourn time      : {1:<8.5f}. Mean sojourn time: {2:<8.5f}. Var: {3:<8.5f}
        Total accumulative service time      : {4:<8.5f}. Mean service time: {5:<8.5f}. Var: {6:<8.5f}
        Total accumulative waiting time      : {7:<8.5f}. Mean waiting time: {8:<8.5f}. Var: {9:<8.5f}""".format(self.number_of_jobs, self.total_sojourn_time, sojourn_mean, sojourn_var, self.total_service_time, service_mean, service_var, self.total_waiting_time, waiting_mean, waiting_var)
        with open('./Simulation_results/' + file_name + '.txt', 'a') as myfile:
            myfile.write(data + "\n")

    def write_to_file_stats(self, file_name):  # pragma: no cover
        self.create_sim_dir()
        if(self.number_of_jobs > 1):
            sojourn_var = (self.second_pass_sojourn - self.total_sojourn_time * self.total_sojourn_time / self.number_of_jobs) / (self.number_of_jobs - 1)
            service_var = (self.second_pass_service - self.total_service_time * self.total_service_time / self.number_of_jobs) / (self.number_of_jobs - 1)
            waiting_var = (self.second_pass_waiting - self.total_waiting_time * self.total_waiting_time / self.number_of_jobs) / (self.number_of_jobs - 1)
        else:
            sojourn_var = 0
            service_var = 0
            waiting_var = 0
        if(self.number_of_jobs > 0):
            sojourn_mean = self.total_sojourn_time / self.number_of_jobs
            service_mean = self.total_service_time / self.number_of_jobs
            waiting_mean = self.total_waiting_time / self.number_of_jobs
        else:
            sojourn_mean = 0
            service_mean = 0
            waiting_mean = 0
        data = """Number of jobs = {0}.
        Total accumulative sojourn time      : {1:<8.5f}. Mean sojourn time: {2:<8.5f}. Var: {3:<8.5f}
        Total accumulative service time      : {4:<8.5f}. Mean service time: {5:<8.5f}. Var: {6:<8.5f}
        Total accumulative waiting time      : {7:<8.5f}. Mean waiting time: {8:<8.5f}. Var: {9:<8.5f}""".format(self.number_of_jobs, self.total_sojourn_time, sojourn_mean, sojourn_var, self.total_service_time, service_mean, service_var, self.total_waiting_time, waiting_mean, waiting_var)
        with open('../data_results/' + file_name + '.txt', 'a') as myfile:
            myfile.write(data + "\n")

    def save_run(self, st):  # pragma: no cover
        f = open('../data_results/simulation_run_for_tests.txt', 'a+')
        pairs = [item for item in zip(self.job_arrival_times, self.job_sizes)]
        pairs.append(st)
        for item in pairs:
            f.write("{},{}\n".format(item[0], item[1]))
        f.close()

    def increment_jobs(self):
        self.number_of_jobs += 1
