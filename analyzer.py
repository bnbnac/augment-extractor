import cv2
import pytesseract

dir = 'downloads/'
file = 'test.mp4' ## may be given from param

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/Cellar/tesseract/5.3.1/bin/tesseract'
custom_config = r'--psm 6' 

relative_x = 0.33
relative_y = 0.1  
relative_w = 0.33
relative_h = 0.3 

threshold_val = 130

cap = cv2.VideoCapture(dir + file)

accuracy = 1
frame_rate = cap.get(cv2.CAP_PROP_FPS)
frame_interval = round(frame_rate * (1 / accuracy))
frame_counter = 1

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if frame_counter % frame_interval == 0:

        height, width, _ = frame.shape
        x = int(relative_x * width)
        y = int(relative_y * height)
        w = int(relative_w * width)
        h = int(relative_h * height)

        roi = frame[y:y+h, x:x+w]
        frame_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        __, img_binary = cv2.threshold(frame_gray, threshold_val, 255, cv2.THRESH_BINARY_INV)

        text = pytesseract.image_to_string(img_binary, lang='kor', config=custom_config)
        text_set = set(text)

        score = 0
        list = ["선", "서", "택", "태"]
        for l in list:
            if (l in text_set):
                score += 1

        if (score >= 2):
            cv2.imwrite('storage/' + 'frame' + str(frame_counter) + '.jpg', frame)
            
    frame_counter += 1

cap.release()
cv2.destroyAllWindows()