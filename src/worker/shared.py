from queue import Queue
import json
import multiprocessing

class ProcessQueue(Queue):
    def __init__(self):
        super().__init__()

    def find_position(self, post_id):
        initial = 0
        current = 0
        for i, el in enumerate(self.queue):
            if str(el[2]) == str(post_id):
                initial = el[3] + 1
                current = i + 1
                break
        return initial, current

    def remove_nth_element(self, n):
        idx = n - 1
        temp_queue = ProcessQueue()

        for _ in range(idx):
            if self.empty():
                raise IndexError("Queue is empty or idx is out of range")
            temp_queue.put(self.get())

        self.get()  # removed

        while not self.empty():
            temp_queue.put(self.get())
    # 다른 데서 이 shared instance를 import 하는 방식을 잘 모르겠어서 일단 이렇게
        while not temp_queue.empty():
            self.put(temp_queue.get())


class CurProcess:
    def __init__(self):
        self.post_id = ''
        self.state = 'standby'
        self.cur_frame = 0
        self.total_frame = 0
        self.quit_flag = 0
        self.event = None

    def is_current_job(self, post_id):
        return self.post_id == post_id

    def done(self):
        self.post_id = ''
        self.state = 'standby'
        self.cur_frame = 0
        self.total_frame = 0
        self.quit_flag = 0
        self.event = None


process_queue = ProcessQueue()
current_processing_info = CurProcess()
frames_queue = multiprocessing.Queue()
results_queue = multiprocessing.Queue()

def load_config(filename):
    with open(filename, 'r') as f:
        config = json.load(f)
    return config


config = load_config('config.json')

LOCAL_DIR = config['LOCAL_DIR']
REMOTE_DIR = config['REMOTE_DIR']
TESSERACT_CMD = config['TESSERACT_CMD']
STORAGE_USER = config['STORAGE_USER']
STORAGE_SERVER = config['STORAGE_SERVER']
SPRING_SERVER = config['SPRING_SERVER']
EXTRACTOR_SERVER = config['EXTRACTOR_SERVER']
NUM_PROCESS = config['NUM_PROCESS']