import queue

task_queue = queue.Queue()

def add_task(data):
    task_queue.put(data)

def get_task():
    return task_queue.get()

def task_done():
    task_queue.task_done()