
### **(개인)** Augment-Extractor**([Github](https://github.com/bnbnac/augment-extractor))**

클라이언트가 영상 게시를 요청하면 [tftad 서버](https://github.com/bnbnac/tftad)는 Augment-Extractor로 관련 정보를 전송합니다. Augment-Extractor는 비디오를 다운받고, 분석하고, 필요한 장면을 추출하여 storage 서버에 저장합니다.

예정: 추출한 장면을 가지고 정답선택 등 사용자와 상호작용 가능한 콘텐츠 개발

## 기술

- Flask, [OpenCV](https://github.com/opencv/opencv), [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

## 특징

- OpenCV와 Tesseract OCR을 이용하여 증강체 선택장면을 추출합니다.([Blog](https://velog.io/@bnbnac/OpenCV%EC%99%80-Tesseract-OCR%EC%9D%84-%EC%9D%B4%EC%9A%A9%ED%95%98%EC%97%AC-%EC%A6%9D%EA%B0%95%EC%B2%B4-%EC%84%A0%ED%83%9D%EC%9E%A5%EB%A9%B4-%EC%B6%94%EC%B6%9C%ED%95%98%EA%B8%B0))
- 추출 장면들을 잘라서 storage 서버에 전송합니다. 그리고 [tftad 서버](https://github.com/bnbnac/tftad)로 완료 request를 전송합니다.
- worker queue를 유지하여 현재 작업 정보 반환하는 기능을 갖습니다.([Blog](https://velog.io/@bnbnac/worker-queue%EB%A5%BC-%EC%9C%A0%EC%A7%80%ED%95%98%EC%97%AC-%ED%98%84%EC%9E%AC-%EC%9E%91%EC%97%85-%EC%A0%95%EB%B3%B4-%EB%B0%98%ED%99%98%ED%95%98%EA%B8%B0))%