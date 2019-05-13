# A general dispatcher.
# Holds information like what policy to use and what servers are available
# May hold additional information


class Dispatcher():
    _policy = None
    _servers = None

    # Initialize a dispatcher with a given policy and a list of available servers
    def __init__(self, policy, servers, *args, **kwargs):
        self._policy = policy
        self._servers = servers

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return True
        return False

    # Takes in a job to decide and the world
    # Makes a decision based on policy to send the job to an available server
    def make_decision(self, param):
        job = param[0]  # Grab the job to be dispatched
        world = param[1]  # Grab the world

        server_id = self._policy.make_decision(self._servers, job)  # Get a server from the list to send job to
        server_to_process = self._servers[server_id]  # Get the instance of the server to process job
        # Now we can schedule the add job into world events, given arrival time and list with job and world and policy
        world.schedule_event(server_to_process.add_job, job._arrival_time, [job, world, self._policy])

    # Later if we want e.g. idle queue of servers or similar, we create methods to create those variables
    # Additional sophisticated methods here later.
