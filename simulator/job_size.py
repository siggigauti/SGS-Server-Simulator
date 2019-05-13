# Represents the service rate at which jobs determine sizes.
# Uses exponential with a given service_rate


class Expo():
    _service_rate = 1
    _rnd_stream = None

    # Initializing the service_rate, defaults to 1
    def __init__(self, service_time, *args, **kwargs):
        self._service_rate = service_time

    # Returns a service time exponentially distributed, given a service rate.
    def get_service_time(self):  # pragma: no cover
        return self._rnd_stream.exponential(1 / self._service_rate)

    def set_random_stream(self, rnd_stream):
        self._rnd_stream = rnd_stream
