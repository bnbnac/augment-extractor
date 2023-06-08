import cv2, os

dir = 'downloads/'
file = 'test.mp4' ## may be given from param

cap = cv2.VideoCapture(dir + file)

frame_rate = cap.get(cv2.CAP_PROP_FPS)
# frame_interval = frame_rate / 2
frame_interval = 1500
frame_counter = 1

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if frame_counter % frame_interval == 0:
        # cv2.imwrite('storage/' + 'frame' + str(frame_counter) + '.jpg', frame)
        pass

    frame_counter += 1

cap.release()
cv2.destroyAllWindows()