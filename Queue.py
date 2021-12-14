from threading import Thread
from time import sleep
from Task import Task
from typing import List
from Browser import Browser
import asyncio


def test(task):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(task.run.start())
    loop.close()


class Queue(Thread):
    def __init__(self):
        super().__init__()
        self.queue: List[Task] = []
        self.running = False

    def run(self):
        self.running = True
        while self.running == True:
            if len(self.queue) == 0:
                sleep(.1)
                continue
            task: Task = self.queue.pop(0)
            test(task)
