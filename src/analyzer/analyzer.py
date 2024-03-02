import cv2
import pytesseract
from typing import List


class VideoAnalyzer:
    def __init__(self, tesseract_cmd: str = '/opt/homebrew/Cellar/tesseract/5.3.2_1/bin/tesseract',
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

    def analyze_video(self, video_path: str, ext: str) -> List[str]:
        cap = cv2.VideoCapture(video_path + '.' + ext)

        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        if frame_rate < self.accuracy:
            print("too high analyzer accuracy")
        skip_frame = round(frame_rate * (1 / self.accuracy))
        frame_counter = 1

        results = []

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            if frame_counter % skip_frame == 0:
                if self._is_aug_selection(frame):
                    results.append(frame_counter)

            frame_counter += 1

        cap.release()
        cv2.destroyAllWindows()

        frame_intervals = self._generate_intervals(
            results, skip_frame, self.accuracy)
        time_intervals = self._frame_intervals_to_timestamps(
            frame_intervals, frame_rate)

        return time_intervals

    def _is_aug_selection(self, frame) -> str:
        height, width, _ = frame.shape
        x = int(self.relative_x * width)
        y = int(self.relative_y * height)
        w = int(self.relative_w * width)
        h = int(self.relative_h * height)

        roi = frame[y:y + h, x:x + w]
        frame_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, frame_binary = cv2.threshold(
            frame_gray, self.threshold_val, 255, cv2.THRESH_BINARY_INV)  # 흑백으로 만들어야 tesseract가 잘 찾음

        text = set(pytesseract.image_to_string(
            frame_binary, lang='kor', config=self.custom_config))

        # criteria에 '증', '강'을 넣으면 이상한 장면을 가지고 옴 'ㅇ' 받침에 약한듯 & 증강선택이 아니라 빌드선택이라고 뜨는 경우가 있음?
        score = sum(1 for l in ['선', '서', '택', '태'] if l in text)

        # 어차피 frame이 많으니까 원치않는 frame을 피하기 위해 2점 이상으로
        return score >= 2

    def _generate_intervals(self, result_frames, skip_frame, accuracy):
        ret = []
        depth = 0
        select_time_limit = 20  # 컷편집 한 영상. 풀영상은 이걸 더 높게. 영상업로드시 컷편집여부를 선택하도록 유도함
        padding = 3 * skip_frame * accuracy

        aug_start = result_frames[0]
        cur = result_frames[0]
        last = -1000

        for f in result_frames[1:]:
            depth += 1
            last, cur = cur, f

            # the time between `last` and `cur` is larger than select_time_limit && number of this bunch of frames are larger than accuracy
            if select_time_limit * (skip_frame * accuracy) < cur - last:
                if depth >= accuracy:
                    print(select_time_limit * (skip_frame * accuracy))
                    ret.extend([aug_start - padding, last + padding])
                    print([aug_start, last])
                depth = 0
                aug_start = cur

        print("reslut_frame" + str(result_frames))
        print("intervals" + str(ret))
        return ret

    def _seconds_to_hh_mm_ss(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "{:02d}:{:02d}:{:02d}".format(int(h), int(m), int(s))

    def _frame_intervals_to_timestamps(self, frame_intervals, frame_rate):
        timestamps = []

        for i in range(0, len(frame_intervals), 2):
            start_frame = frame_intervals[i]
            end_frame = frame_intervals[i + 1]

            start_time = start_frame / frame_rate
            end_time = end_frame / frame_rate

            timestamps.append(self._seconds_to_hh_mm_ss(start_time))
            timestamps.append(self._seconds_to_hh_mm_ss(end_time))

        return timestamps


# analyzer = VideoAnalyzer()
# interv = analyzer._generate_intervals([705, 720, 735, 765, 795, 810, 825, 840, 870, 885, 900, 915,
#                                        930, 945, 6795, 6810, 6825, 6840, 6855, 6870, 6975, 6990, 7020, 7035, 10965, 10980, 11700, 16725], 15, 2.0)
# ts = analyzer._frame_intervals_to_timestamps(interv, 30)
# print(interv)
# print(ts)
# interval = analyzer._generate_intervals(
#     [720, 810, 840, 870, 900, 930, 6810, 6840, 6870, 6990, 7020, 10980, 11700])
# totime = analyzer._frame_intervals_to_timestamps(interval, 30)
# print(interval)
# print(totime)
# result_frames = analyzer.analyze_video(video_path='../../downloads/low/abcdef', ext='mp4')
# generator(result_frames)
