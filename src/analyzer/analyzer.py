import multiprocessing
import sys
import datetime
import cv2
import os
import pytesseract
from typing import List
from src.worker.shared import current_processing_info, TESSERACT_CMD, NUM_PROCESS, LOCAL_DIR
from src.worker.shared import frames_queue, results_queue
from src.exception.exception import RequestedQuitException
from src.deleter.deleter import delete_local_directory


class VideoAnalyzer:
    def __init__(self, tesseract_cmd: str = TESSERACT_CMD,
                 custom_config: str = r'--psm 6',
                 relative_x: float = 0.33, relative_y: float = 0.1,
                 relative_w: float = 0.33, relative_h: float = 0.3,
                 threshold_val: int = 130, accuracy: float = 2.0):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.custom_config = custom_config
        self.relative_x = relative_x
        self.relative_y = relative_y
        self.relative_w = relative_w
        self.relative_h = relative_h
        self.threshold_val = threshold_val
        self.accuracy = accuracy
        self.frames_dir = None
        self.frame_rate = None
        self.skip_frame = None

    def analyze(self, video_path: str, ext: str, member_id: str, post_id: str) -> List[str]:
        current_processing_info.state = 'on analysis'

        frame_count = self.save_capture_frames(video_path, ext, member_id, post_id)
        current_processing_info.total_frame = frame_count
        
        frame_intervals = self.get_time_interval_from_video(member_id, post_id)
        
        return self._frame_intervals_to_time_intervals(frame_intervals)

    def multi_tesseract(self, member_id, post_id):
        while True:
            if current_processing_info.quit_flag == 1:
                delete_local_directory(member_id, post_id)
                raise RequestedQuitException
            
            current_processing_info.cur_frame = frames_queue.qsize()

            frame_count = frames_queue.get()
            if frame_count is None:
                break

            img_path = f'{self.frames_dir}/frame_{frame_count}.jpg'

            if self._is_aug_selection(img_path=img_path):
                results_queue.put(frame_count)

    def img_post_work(self, frame):
        height, width, _ = frame.shape
        x = int(self.relative_x * width)
        y = int(self.relative_y * height)
        w = int(self.relative_w * width)
        h = int(self.relative_h * height)

        roi = frame[y:y + h, x:x + w]
        frame_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, frame_binary = cv2.threshold(
            frame_gray, self.threshold_val, 255, cv2.THRESH_BINARY_INV)

        return frame_binary


    def save_capture_frames(self, video_path: str, ext: str, member_id: str, post_id: str) -> List[str]:
        start_time = datetime.datetime.now()
        print("CAPTURE_SAVE Start time:", start_time, flush=True)
        cap = cv2.VideoCapture(f'{video_path}.{ext}')

        current_processing_info.total_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frame_rate = cap.get(cv2.CAP_PROP_FPS)

        if self.frame_rate < self.accuracy:
            print("too high analyzer accuracy")
            raise RequestedQuitException

        self.skip_frame = round(self.frame_rate * (1 / self.accuracy))
        frame_count = 0
        self.frames_dir = f'{LOCAL_DIR}/downloads/{member_id}/{post_id}/temp'
        os.makedirs(self.frames_dir, exist_ok=True)

        while True:
            ret = cap.grab()
            if not ret:
                break
            if frame_count % self.skip_frame == 0:
                ret, frame = cap.retrieve()

                frames_queue.put(frame_count)
                frame_filename = os.path.join(self.frames_dir, f"frame_{frame_count}.jpg")

                frame_binary = self.img_post_work(frame)
                cv2.imwrite(frame_filename, frame_binary)

            frame_count += 1

        cap.release()
        cv2.destroyAllWindows()
        end_time = datetime.datetime.now()
        print("CAPTURE_SAVE End time:", end_time, flush=True)

        return frame_count
    

    def get_time_interval_from_video(self, member_id: str, post_id: str) -> List[str]:
        start_time = datetime.datetime.now()
        print("AUG_SELECTION Start time:", start_time, flush=True)

        for _ in range(NUM_PROCESS):
            frames_queue.put(None)

        processes = []
        try:
            for _ in range(NUM_PROCESS):
                process = multiprocessing.Process(target=self.multi_tesseract, args=(member_id, post_id))
                process.start()
                processes.append(process)
        except RequestedQuitException:
            for process in processes:
                process.terminate()
            delete_local_directory(member_id, post_id)
            raise

        for process in processes:
            process.join()
            
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        print(f"***************CAUGHT FRAMES{results}***************", flush=True)
        results.sort()
        frame_intervals = self._generate_intervals(
        results)
        print(f"***************RETURN{frame_intervals}***************", flush=True)

        return frame_intervals

    def _is_aug_selection(self, img_path) -> bool:
        frame = cv2.imread(img_path)

        text = set(pytesseract.image_to_string(
            frame, lang='kor', config=self.custom_config))

        score = sum(1 for l in ['선', '서', '택', '태'] if l in text)

        os.remove(img_path)
        return score >= 2

    def _generate_intervals(self, result_frames):
        ret = []
        result_frames.append(sys.maxsize)
        depth = 0
        aug_select_time_limit = 20  # 컷편집 한 영상. 풀영상은 이걸 더 높게. 영상업로드시 컷편집여부를 선택하도록 유도함
        padding = 3 * self.skip_frame * self.accuracy

        aug_start = result_frames[0]
        cur = result_frames[0]
        last = -1000

        for f in result_frames[1:]:
            depth += 1
            last, cur = cur, f

            if aug_select_time_limit * (self.skip_frame * self.accuracy) < cur - last:
                if depth > self.accuracy * 3:
                    ret.extend([max(0, aug_start - padding * 7), min(current_processing_info.total_frame, last + padding)])
                depth = 0
                aug_start = cur
        return ret

    def _seconds_to_hh_mm_ss(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "{:02d}:{:02d}:{:02d}".format(int(h), int(m), int(s))

    def _frame_intervals_to_time_intervals(self, frame_intervals):
        time_intervals = []

        for i in range(0, len(frame_intervals), 2):
            start_frame = frame_intervals[i]
            end_frame = frame_intervals[i + 1]

            start_time = start_frame / self.frame_rate
            end_time = end_frame / self.frame_rate

            time_intervals.append(self._seconds_to_hh_mm_ss(start_time))
            time_intervals.append(self._seconds_to_hh_mm_ss(end_time))

        return time_intervals
