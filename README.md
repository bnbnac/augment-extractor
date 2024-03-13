어떻게든 돌아가게만 만든 서버입니다

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

analysis 요청이 몰려들어올 때 동작?
어차피 1080p가 있을텐데 best로 할필요가 있을까
https://www.youtube.com/watch?v=VpIDjGs5_bI
이거 2번째증강 안잡혔음 acc 더 올려야....

ffmpeg가 실패했을때의 return
현재 analysis 시간대

{postid} dir가 없어도 cut이 잘 생성되는지 - os.확인작업?
download.py와 existence

헉. 인터발이 안잡혀서 컷이 없을때 8080:/extractor/complete - 500
컷이 하나일때 알고리즘 수정

todo: analyzer나 cutter에서 뭔가 실패하면 최후순위 큐를 만들어서 거기에 넣자. 이 큐에 있는건 original queue가 비었을때만 처리하도록
exception 발생시 springboot로 뭘 보낼지
work 객체 도입?

비디오가 너무 크면 {spring-server}/extractor/complete 에다가 안한다고 보내야함
보내는 형식 process_video() 하단 참고

시점을 로깅해야겠는데 timestamp

리팩토링 언제함 ㅋㅋㅋ
