import cv2
import pytesseract
from typing import List


class VideoAnalyzer:
    def __init__(self, tesseract_cmd: str = '/opt/homebrew/Cellar/tesseract/5.3.2_1/bin/tesseract',
                 custom_config: str = r'--psm 6',
                 relative_x: float = 0.33, relative_y: float = 0.1,
                 relative_w: float = 0.33, relative_h: float = 0.3,
                 threshold_val: int = 130, accuracy: float = 1.0):
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
        frame_interval = round(frame_rate * (1 / self.accuracy))
        frame_counter = 1

        result_frames = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_counter % frame_interval == 0:
                processed_frame = self.process_frame(frame, frame_counter)
                if processed_frame:
                    result_frames.append(frame_counter)

            frame_counter += 1

        cap.release()
        cv2.destroyAllWindows()

        return self._generate_intervals(result_frames)

    def process_frame(self, frame, frame_counter) -> str:
        height, width, _ = frame.shape
        x = int(self.relative_x * width)
        y = int(self.relative_y * height)
        w = int(self.relative_w * width)
        h = int(self.relative_h * height)

        roi = frame[y:y + h, x:x + w]
        frame_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, frame_binary = cv2.threshold(
            frame_gray, self.threshold_val, 255, cv2.THRESH_BINARY_INV)

        text = set(pytesseract.image_to_string(
            frame_binary, lang='kor', config=self.custom_config))

        # criteria에 '증', '강'을 넣으면 이상한 장면을 가지고 옴 'ㅇ' 받침에 약한듯 & 증강선택이 아니라 빌드선택이라고 뜨는 경우가 있음?
        score = sum(1 for l in ['선', '서', '택', '태'] if l in text)

        # 어차피 frame이 많으니까 원치않는 frame을 피하기 위해 2점 이상으로
        return score >= 2

    def _generate_intervals(self, result_frames):
        ret = []

        aug_start = result_frames[0]
        cur = result_frames[0]
        last = -1000

        for f in result_frames[1:]:
            distance = cur - last
            last, cur = cur, f

            if distance * 30 < cur - last:
                ret.extend([aug_start, last])
                aug_start = cur

        ret.extend([aug_start, result_frames[-1]])
        return ret


# analyzer = VideoAnalyzer()
# interval = analyzer._generate_intervals(
#     [720, 810, 840, 870, 900, 930, 6810, 6840, 6870, 6990, 7020, 10980, 11700])
# print(interval)
# result_frames = analyzer.analyze_video(video_path='../../downloads/low/abcdef', ext='mp4')
# generator(result_frames)
