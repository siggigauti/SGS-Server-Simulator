#!/usr/bin/env python3
from heapq import heappush, heappop
# This class represents the global state of the simulation
# Holds e.g. the scheduled events in a priority queue
# Has methods to schedule a new event or process the next event.


class Global():

    ##################################
    # Global event scheduler         #
    # A priority queue for events    #
    ##################################
    eventQueue = []
    _stats = None

    def __init__(self, stats, *args, **kwargs):
        self._stats = stats
        self.eventQueue = []

    # Main scheduler function.
    # Adds an event (Arrival, Departure, Process ..) to the main eventQueue
    # The priority heapqueue will put the events in order of time
    # param is a list of e.g. [server/dispatcher, job, ...]
    def schedule_event(self, func, time, param):
        if time < 0:
            raise ValueError('time cannot be negative')
        heappush(self.eventQueue, [time, param, func])

    # Takes the next event from event scehduler and processes it
    def process_event(self):
        if(self.eventQueue):  # We have a queue
            time, param, func = heappop(self.eventQueue)  # Pop the next event off the top
            func(time, param)  # runs the function with parameter(s) and time from the queue

    def next_event(self):
        if not self.eventQueue:  # pragma: no cover
            return -1
        e = self.eventQueue[0]  # Get the next event (a list with [time, param, function])
        return e[0]  # Get the 0th place (time) from the event and return it (returning time of next event)
