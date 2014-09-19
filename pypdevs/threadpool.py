# Copyright 2014 Modelling, Simulation and Design Lab (MSDL) at 
# McGill University and the University of Antwerp (http://msdl.cs.mcgill.ca/)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A threadpool to process incomming messages over MPI with a fixed number of
(already running) threads.

Based on threadpool implementation found at http://stackoverflow.com/
questions/3033952/python-thread-pool-similar-to-the-multiprocessing-pool
"""
try:
    import Queue as queue
except ImportError:
    import queue
from threading import Thread

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        """
        Constructor

        :param tasks: queue containing tasks to execute
        """
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        """
        Run the worker thread
        """
        while 1:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)
            finally:
                self.tasks.task_done()

class ThreadPool(object):
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        """
        Constructor

        :param num_threads: number of threads to start
        """
        self.tasks = queue.Queue()
        self.num_threads = num_threads
        for _ in range(num_threads): 
            Worker(self.tasks)

    def __setstate__(self, state):
        """
        For pickling
        """
        # Obj will be empty, accept it though
        self.__init__(state)

    def __getstate__(self):
        """
        For pickling
        """
        # A queue is unpicklable...
        return self.num_threads

    def add_task(self, func, *args, **kwargs):
        """
        Add a task to the queue

        :param func: function to execute
        """
        self.tasks.put((func, args, kwargs))
