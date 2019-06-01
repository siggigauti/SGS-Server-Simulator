import numpy as np
import scipy.stats


def confidence_interval(data, confidence=1.96):
    a = 1.0 * np.array(data)
    n = len(a)
    std = np.std(a, dtype=np.float64)
    m = np.mean(a, dtype=np.float64)
    se = std / np.sqrt(n)
    h = se * confidence
    return m, m - h, m + h, h


def main(rho):
    data = None
    with open('../data_results/new_NO_matrix_mean_results_rho_' + str(rho) + '.txt', 'r') as myfile:
        data = myfile.read().splitlines()
    data_sojourn = [float(x.split(',')[0]) for x in data]
    data_service = [float(x.split(',')[1]) for x in data]
    data_waiting = [float(x.split(',')[2]) for x in data]

    print("NO Sojourn data: {}".format(confidence_interval(data_sojourn)))
    print("NO Waiting data: {}".format(confidence_interval(data_waiting)))
    print("NO Service data: {}".format(confidence_interval(data_service)))
    no_sojourn_mean = confidence_interval(data_sojourn)
    no_waiting_mean = confidence_interval(data_waiting)
    no_service_mean = confidence_interval(data_service)

    data = None
    with open('../data_results/SED_mean_results_rho_' + str(rho) + '.txt', 'r') as myfile:
        data = myfile.read().splitlines()
    data_sojourn = [float(x.split(',')[0]) for x in data]
    data_service = [float(x.split(',')[1]) for x in data]
    data_waiting = [float(x.split(',')[2]) for x in data]

    print("SED Sojourn data: {}".format(confidence_interval(data_sojourn)))
    print("SED Waiting data: {}".format(confidence_interval(data_waiting)))
    print("SED Service data: {}".format(confidence_interval(data_service)))
    sed_sojourn_mean = confidence_interval(data_sojourn)
    sed_waiting_mean = confidence_interval(data_waiting)
    sed_service_mean = confidence_interval(data_service)

    diff_sojourn_mean = no_sojourn_mean[0] - sed_sojourn_mean[0]
    diff_waiting_mean = no_waiting_mean[0] - sed_waiting_mean[0]
    diff_service_mean = no_service_mean[0] - sed_service_mean[0]
    print("Sojourn performance increase from SED to NO: {}".format((diff_sojourn_mean / no_sojourn_mean[0]) * 100))
    print("Waiting performance increase from SED to NO: {}".format((diff_waiting_mean / no_waiting_mean[0]) * 100))
    print("Service performance increase from SED to NO: {}".format((diff_service_mean / no_service_mean[0]) * 100))


def rnd_stats():
    data = None
    with open('../data_results/RND.txt', 'r') as myfile:
        data = myfile.read().splitlines()
    data_sojourn = [float(x.split(',')[0]) for x in data]
    data_service = [float(x.split(',')[1]) for x in data]
    data_waiting = [float(x.split(',')[2]) for x in data]
    print("RND Sojourn data: {}".format(confidence_interval(data_sojourn)))
    print("RND Waiting data: {}".format(confidence_interval(data_waiting)))
    print("RND Service data: {}".format(confidence_interval(data_service)))


def jsq_stats():
    data = None
    with open('../data_results/JSQ.txt', 'r') as myfile:
        data = myfile.read().splitlines()
    data_sojourn = [float(x.split(',')[0]) for x in data]
    data_service = [float(x.split(',')[1]) for x in data]
    data_waiting = [float(x.split(',')[2]) for x in data]
    print("JSQ Sojourn data: {}".format(confidence_interval(data_sojourn)))
    print("JSQ Waiting data: {}".format(confidence_interval(data_waiting)))
    print("JSQ Service data: {}".format(confidence_interval(data_service)))


if __name__ == '__main__':
    main(0.95)
