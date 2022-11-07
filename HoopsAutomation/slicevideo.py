#==================

#  file name    : slice_video.py
#  author.      : iman jefferson

#.    created date:  12-09-202
# description :  creates time stamp windows and slices up videos


# 
#=========


import numpy as np
import cv2

def crete_time_stamp_windows(made_basket_start_frames, seconds_before, seconds_after, fps):
    """
    feed in a list of frames and how many seconds before and after as well as fps
    returns a dictionary with all the start frames and all the end frmaes for slicing
    """
    
    start_frames = np.array(made_basket_start_frames) - (seconds_before*fps)
    end_frames = np.array(made_basket_start_frames) + (seconds_after*fps)
    
    return_data = {"start_frames": start_frames, "end_frames": end_frames}
    return(return_data)
    
    
def video_slicer(filepath, save_path, start_indexes, end_indexes):
"""

taes in avideo path, a save path, start and end indexes
saves a video thats cut at the specific indexes
"""
cap= cv2.VideoCapture(filepath)

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
out = cv2.VideoCapture(save_path, cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width, frame_height))

if len(start_indexes) != len(end_indexes):
    return("Time stamps must be at the same length")
    
basket_counter = 0
frame_counter = 0
while True:
    ret, rame = cap.read()
    if not ret:
        # if no more frames then break
        break
        
    if not ret:
    
    if frame_counter >= start_indexes[basket_counter] and frame_counter <= end_indexes[basket_counter]:
        # if we are in a basket then save that frame_counterout.write(frame)
        elif frame_counter > end_indexes[basket_counter]:
        # if we just left a basket then increment our basket counter
        basket_counter += 1
        
    frame_counter += 1
    
cap.release()
out.release()
print("{} clips were sliced".format(str(basket_counter)))
print("File Saved to {}".format(save_path))