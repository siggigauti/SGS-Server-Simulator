import math
import numpy as np


class Policy():
    def __init__(self, policyseed, *args, **kwargs):  # pragma: no cover
        pass

    def make_decision(self, servers, job):  # pragma: no cover
        pass


class RND(Policy):
    _rnd_stream = None

    def __init__(self, policyseed=None, *args, **kwargs):
        if policyseed is not None:
            self._rnd_stream = np.random.RandomState(policyseed)
        else:
            self._rnd_stream = np.random.RandomState()

    # Usage: policy.make_decision(servers)
    # Before: servers is a list of available servers to route to.
    # After: Return an index that points to the location of the server to be routed to.
    def make_decision(self, servers, job):
        return self._rnd_stream.randint(0, len(servers))  # pick a random server from given list


class ShortestQueue(Policy):
    _rnd_stream = None

    def __init__(self, policyseed=None, *args, **kwargs):
        if policyseed is not None:
            self._rnd_stream = np.random.RandomState(policyseed)
        else:
            self._rnd_stream = np.random.RandomState()

    def make_decision(self, servers, job):
        queues = []
        for server in servers:
            queues.append(server._total_jobs)

        return min(range(len(queues)), key=queues.__getitem__)


class SED(Policy):
    _rnd_stream = None

    def __init__(self, policyseed=None, *args, **kwargs):
        if policyseed is not None:
            self._rnd_stream = np.random.RandomState(policyseed)
        else:
            self._rnd_stream = np.random.RandomState()

    def make_decision(self, servers, job):
        best_so_far = 9999999999
        server_id = 0
        counter = 0
        for server in servers:
            expected_delay = (server._total_jobs + 1) / server._service_rate
            if expected_delay < best_so_far:
                server_id = counter
                best_so_far = expected_delay
            counter += 1
        return server_id


class Qlearning(Policy):
    Q = {}  # [(state, action): value]
    v_new = None
    v = {}  # [state: value]
    v2 = {}
    state_counter = {}
    j = 0           # step counter
    x = None        # current state
    n = None        # previous state
    t = 0           # time between visits in S
    c = 0           # incurred cost between visits
    T = 0           # Total discounted time
    C = 0           # Total discounted costs
    last_event = 0  # Time of last event (When on the timeline)
    S = None
    nS = None
    uS = None       # A collection of all states under S
    A = None
    nA = None
    sim_time = 0
    n_servers = 0  # number of servers
    servers = []  # list of the servers
    a = -2  # Previous action within box S.
    r = 0
    weights = [0, 1]
    _rnd_stream = None

    #######################
    ## UTILITY FUNCTIONS ##
    #######################

    # Returns true if x is in A
    def x_in_a(self):
        for i in range(0, self.n_servers):  # For every server
            if self.x[i] > self.A[i]:  # Check if the point is outside the A area
                return False
        if self.x in self.nA:  # Should be [x,y,z] in [[x1,y1,z1], .., [xN, yN, zN]]
            return False
        return True

    # Returns true if x is in S
    def x_in_s(self):
        for i in range(0, self.n_servers):
            if self.x[i] > self.S[i]:
                return False
        if self.x in self.nS:  # Should be [x,y,z] in [[x1,y1,z1], .., [xN, yN, zN]]
            return False
        return True

    # Returns the position of server in servers, -1 if not exists
    def find_server_pos(self, server):
        i = 0
        for s in self.servers:
            if server is s:
                return i
            i += 1
        return -1

    # Used to generate permutations of all 'states' under S
    def getlist(self):
        r = []
        c = [0] * len(self.S)
        while 1:
            r.append(c[:])
            for i in reversed(range(len(self.S))):  # if len(S) = 10, then its 9,8,7,..,1,0
                c[i] += 1
                if(c[i] <= self.S[i]):
                    break
                c[i] = 0
                if i is 0:
                    return r

    def alt_jsq(self, servers):
        queues = []
        for server in servers:
            queues.append(server._total_jobs)
        return min(range(len(queues)), key=queues.__getitem__)

    def enable_qlearn_on_servers(self):
        for server in self.servers:
            server._qenabled = True

    def alt_sed(self, servers):
        best_so_far = 9999999999
        server_id = 0
        counter = 0
        for server in servers:
            expected_delay = (server._total_jobs + 1) / server._service_rate
            #print('expected_delay for server {} is {} where totaljobs = {} and service rate = {}'.format(server, expected_delay, server._total_jobs, server._service_rate))
            if expected_delay < best_so_far:
                server_id = counter
                best_so_far = expected_delay
            counter += 1
        #print('The choice was {}'.format(server_id))
        return server_id

    # Takes a list of values, returns the indx of the minimum. Random in case of tie.
    def get_min_value(self, values):
        indxs = []
        for indx, item in enumerate(values):
            if item == min(values):
                indxs.append(indx)
        return self._rnd_stream.choice(indxs)

    #######
    # S = [2,6,1,3]  four servers, max jobs for each one (boundary)
    # nS = [[1,2,1,1], [1,3,1,1]]  a list of states that are excluded from S
    # nA = ...                     a list of states that are excluded from A
    #######
    def __init__(self, S, nS, nA, sim_time, list_of_servers, policyseed=None, *args, **kwargs):
        # TODO: Add way to set weights of exploration (optional kwarg)
        # E.g. default its equal chances (must be done programatically), o.w. can have user provided weights list.
        if policyseed is not None:
            self._rnd_stream = np.random.RandomState(policyseed)
        else:
            self._rnd_stream = np.random.RandomState()
        self.S = S
        tmp = []
        for i in range(0, len(S)):
            tmp.append(S[i] - 1)
        self.A = tmp  # Basically the border of S
        self.nS = nS
        self.nA = nA
        self.sim_time = sim_time
        self.n_servers = len(S)  # How many servers
        self.uS = self.getlist()
        for u in self.uS:  # For every state under S
            # for j in range(0, self.n_servers): # Go through every server
            #    self.Q[str((u,j))] = 0 # Set the Q of state, server to 0 (initialization)
            self.v[str(u)] = 0  # Same for the value of the state
            self.v2[str(u)] = 0
            self.state_counter[str(u)] = 0
        self.x = [0] * self.n_servers  # initialize the x
        self.servers = list_of_servers
        self.enable_qlearn_on_servers()
        #self.state_counter[self.uS[0]] = 1
        self.v_new = np.zeros([x + 1 for x in S])  # Create an ndarray with same boundary as S.

    # Updating the t and c
    def first_part(self, job, arrival):
        dtime = 0  # Time that has elapsed between last event and this event.
        if arrival is True:  # If its an arrival
            dtime = job._arrival_time - self.last_event
            self.t += dtime
            self.last_event = job._arrival_time

        else:  # It's a departure
            dtime = job._departure_time - self.last_event
            self.t += dtime
            self.last_event = job._departure_time
        if dtime < 0:
            print('delta time is below 0, ERROR')
        self.c += dtime * sum(self.x)

    # Arrival
    def make_decision(self, servers, job):

        k = -2  # need to initialize
        self.first_part(job, True)  # Call first part as arrival
        if self.x_in_s():
            if self.x_in_a():  # Check if in subset A

                explore = 1 if self._rnd_stream.rand() <= 0.1 else 0  # As an exponential decay.
                if explore:
                    k = self._rnd_stream.choice(self.weights)
                else:
                    values = []
                    for j in range(0, self.n_servers):  # Step in every direction
                        dx = self.x[:]  # copy state x
                        dx[j] += 1   # dx = new state in direction j
                        values.append(self.v2[str(dx)])  # Add the value function for that step
                    k = self.get_min_value(values)

            else:  # We're on the border (not in A, but in S)
                # For weighted random!
                #k = self._rnd_stream.choice(self.weights)
                k = self.alt_jsq(servers)
            self.a = k
            # We've made a decision,  if the new decision leaves the old state inside the 'box' then we update the n.
            self.n = self.x[:]  # Updating n to be x
        else:  # We're outside S
            #k = self._rnd_stream.choice(self.weights)
            k = self.alt_jsq(servers)
        if(k == -2):
            print('INVALID K, ABORT')  # MAKE INTO TEST

        self.x[k] += 1  # e_k is adding job to server k. (1,1) <- (1,1) + (0,1) = (1,2)
        self.second_part()
        return k

    # Called by server to update when departure
    def departure_update(self, server, job):
        self.first_part(job, False)
        i = self.find_server_pos(server)
        if self.x_in_s():
            self.a = -1
            self.n = self.x[:]  # if state before departing, is in S, then update n.
        self.x[i] -= 1  # update to new state in 'x'
        self.second_part()

    def second_part(self):
        if self.x_in_s():

            self.j += 1
            self.T = self.T + self.t
            self.C = self.C + self.c
            self.r = self.C / self.T
            alpha = math.pow(math.e, ((-10 * self.T) / self.sim_time))
            #alpha = 0.1
            n = str(self.n)  # this is the prev state inside box.
            x = str(self.x)  # this is the new state inside box.
            self.state_counter[x] += 1
            # if True:# self.a == -1: #This happens when we have departure and previous state is inside S
            #    for j in range(0, self.n_servers):
            #        self.Q[str((self.n,j))] = ((1 - alpha)*self.Q[str((self.n,j))] + alpha*(self.c - self.t * self.r + self.v2[x])) # n is prev state, x is new state
            # else: # We're inside A and S, and we made an active decision.
            # only updating the acted upon server
            #    self.Q[str((self.n,self.a))] = ((1 - alpha)*self.Q[str((self.n,self.a))] + alpha*(self.c - self.t * self.r + self.v2[x])) ##CHEATING
            #value_update = []
            # Get all the values from previous state for each action (server) we can take
            # for j in range(0, self.n_servers):
            #    value_update.append(self.Q[str((self.n,j))])
            #self.v[n] = min(value_update)
            #self.v_new[self.n] = (1-alpha)*self.v_new[self.n] + alpha*(self.c - self.r*self.t + self.v_new[self.x])
            self.v2[n] = (1 - alpha) * self.v2[n] + alpha * (self.c - self.r * self.t + self.v2[x])
            if True:
                #    delta = self.v['[0, 0]'] # We get the delta by the value in this state.
                delta1 = self.v2[str([0] * self.n_servers)]
                for k in self.uS:  # For each state under the boundry S.
                    #        self.v[str(k)] = self.v[str(k)] - delta # We subtract the delta from each states value
                    self.v2[str(k)] = self.v2[str(k)] - delta1  # We subtract the delta from each states value
                    # self.v_new[k] = self.v_new[k] - delta1 # We subtract the delta from each states value

            #        for j in range(0, self.n_servers):
            #            self.Q[str((k,j))] = self.Q[str((k,j))] - delta
            self.t = 0  # We reset because we're inside S
            self.c = 0  # --||--
        else:
            if self.a is -1:
                print('abort something wrong here.')


class NO_Matrix(Policy):
    decision_matrix = None
    backup_policy = None

    def __init__(self, matrix, policyseed=None, backup_policy=None, *args, **kwargs):
        if policyseed is not None:
            print(policyseed)
            self._rnd_stream = np.random.RandomState(policyseed)
        else:
            self._rnd_stream = np.random.RandomState()
        self.decision_matrix = matrix
        self.backup_policy = backup_policy

    def make_decision(self, servers, job):
        state = []  # current state
        for server in servers:
            state.append([server._total_jobs])
        try:
            choice = self.decision_matrix[tuple(state)]
            return choice[0, 0]
        except Exception as e:
            choice = self.backup_policy.make_decision(servers, job)
            return choice
