## dependencies

[tesseract](https://github.com/tesseract-ocr/tesseract)
[yt-dlp(pip)](https://github.com/yt-dlp)
[opencv(pip)](https://github.com/opencv)

### todo

virtual env
경로(다운로드, tesseract 모듈 등)를 sys env에서 가져오자

처리속도와의 trade off: 화질(검출력), accuracy(검사하는 프레임 수)
안전장치로 최대 interval 길이도 정해놓고

analyzer.\_generate_intervals은 컷편집 여부를 인수로 받아야함. 조건문을 통해 컷편집 안된 풀영상인 경우 select_time_limit을 높여야함
왜 Analyzer는 class로 했더라?

webm, mp4 인풋아웃풋과 처리속도?
