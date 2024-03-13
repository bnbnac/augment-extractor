from queue import Queue

process_queue = Queue()


class Cur_Process:
    def __init__(self):
        self.post_id = ''
        self.state = 'standby'
        self.cur_frame = 0
        self.total_frame = 0
        self.quit_flag = 0

    def done(self):
        self.post_id = ''
        self.state = 'standby'
        self.cur_frame = 0
        self.total_frame = 0
        self.quit_flag = 0


current_processing_info = Cur_Process()
