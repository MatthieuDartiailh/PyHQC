# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 23:13:00 2013

@author: Matthieu
"""

from threading import Thread
from time import sleep

class ConsumerThread(Thread):

    interrupt = False

    def __init__(self, queue):
        super(ConsumerThread, self).__init__()
        self.setDaemon(True)
        self.queue = queue

    def run(self):
        while not self.interrupt:
            if not self.queue.empty():
                action_dict = self.queue.get()
                target = action_dict['target']
                args = ()
                kwargs = {}
                if action_dict.has_key('args'):
                    args = action_dict['args']
                if action_dict.has_key('kwargs'):
                    kwargs = action_dict['kwargs']
                target(*args, **kwargs)
                self.queue.task_done()
            else:
                sleep(0.1)