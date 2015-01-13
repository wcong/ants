# encoding=utf8
__author__ = 'wcong'
from ants.utils.misc import load_object
from queuelib import PriorityQueue
from twisted.internet import defer


class SchedulerServer():
    '''
    schedule server
    send request to client
    accept request result send to client
    '''

    def __init__(self, settings):
        self.settings = settings
        self.mq_class = load_object(settings['SCHEDULER_MEMORY_QUEUE'])
        self.mqs = PriorityQueue(self.priority)
        self.status = ScheduleStatus()

    def has_pending_requests(self):
        return len(self) > 0

    def push_queue_request(self, request):
        self._mq_push(request)
        self.status.add_push_queue()

    def next_request(self):
        request = self.mqs.pop()
        if request:
            self.status.add_pop_queue()
        return request

    def __len__(self):
        return len(self.mqs)

    def _mq_push(self, request):
        self.mqs.push(request, -request.priority)

    def priority(self, priority):
        return self.mq_class()


class SchedulerClient():
    def __init__(self, settings):
        self.settings = settings
        mq_class = load_object(settings['SCHEDULER_MEMORY_QUEUE'])
        self.mqs = PriorityQueue(mq_class())
        self.status = ScheduleStatus()

    def has_pending_requests(self):
        return len(self) > 0

    def push_queue_request(self, request):
        self._mq_push(request)
        self.status.add_push_queue()

    def next_request(self):
        request = self.mqs.pop()
        if request:
            self.status.add_pop_queue()
        return request

    def __len__(self):
        return len(self.mqs)


    def _mq_push(self, request):
        self.mqs.push(request, -request.priority)


class ScheduleStatus():
    def __init__(self):
        self.queue_type = 'memory'
        self.push_queue = 0
        self.pop_queue = 0

    def add_push_queue(self):
        self.push_queue += 1

    def add_pop_queue(self):
        self.pop_queue += 1