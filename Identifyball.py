#import OpenCV
import cv2

#read the video file into Python
cap = cv2.VideoCapture('your_video.mp4')

#create a convolutional neural network
model = cv2.createCascadeClassifier('path_to_model')

while True:
	#read the frame
	ret, frame = cap.read()
	if not ret:
		break
	
	#detect the sports balls in the frame
	balls = model.detectMultiScale(frame, 1.3, 5)
	
	#display the detected sports balls in the output
	for (x,y,w,h) in balls:
		cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
	
	cv2.imshow("Frame", frame)
	
	#exit loop if 'q' is pressed
	key = cv2.wait
