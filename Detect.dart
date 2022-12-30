import 'dart:ui';
import 'package:firebase_ml_vision/firebase_ml_vision.dart';

// Create the FaceDetector
final FaceDetector faceDetector = FirebaseVision.instance.faceDetector();

// Get the video frames and detect the players
for (int i = 0; i < game.videoFrames.length; i++) {
  final FirebaseVisionImage visionImage = FirebaseVisionImage.fromBytes(
    game.videoFrames[i],
  );

  // Detect the faces in the image
  faceDetector.processImage(visionImage).then((result) {
    if (result.length > 0) 
###


based on their position.
#
#   The script is designed to work with the flutter_detect_players sample project and the video file 'sports-video.mp4'.  It uses a custom classifier created using the flutter_create_classifier sample and identifies players in a sports video based on their position.  After identifying all players, it assigns them unique name tags that are displayed in the top left corner of each player's face box as well as an overlayed text label below each person's face box.
#
#   This script was tested with Python 3.6 and OpenCV 3.1.0


import cv2 # opencv-python library for image processing functions (e.g., thresholding)
import numpy as np # numpy library for array operations (e.g., reshape)


def detectPlayers(frame):

    # load trained cascade classifiers from xml files into memory: eyes, nose, mouth, ears, etc...    
    eyeCascade = cv2.CascadeClassifier('haarcascades/haarcascade_eye')         # eye detection classifier (for detecting eyes)    
    noseCascade = cv2.CascadeClassifier('haarcascades/haarcascade_mcs_nose')    # nose detection classifier (for detecting noses)    
    mouthCascade = cv2.CascadeClassifier('haarcascades/Mouth')                   # mouth detection classifier (for detecting mouths)    

    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)                          # convert frame to grayscale format for faster processing speed     

    faces = faceDetect(grayFrame, eyeCascade, noseCascade, mouthCascade)        # detect faces in input frame using pre-trained haar cascades      

    if len(faces):                                                              # if at least one face is detected:            

        for i in range(len(faces)):                                             # loop through all detected faces:              

            x1=int((faces[i][0]+faces[i][1])/3); y1=int((faces[i][3]+faces[i][4])/3); w=abs((x1+w)-x1); h=abs((y1+h)-
