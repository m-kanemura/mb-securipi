""" credit --- https://www.youtube.com/watch?v=T-7OSD5a-88 """

#CONTINUE working on:
# - adjust motion capture sensitivity (watch video) DONE
# - recapture static frame after a period of time (for room brightness adjustment) DONE
# - consider using date time??? instead of started_count DONE
# - consider sending email using email when motion is detected. DONE
# - have to make a google account DONE
# - Save video to google drive (use google api)? DONE
# - Send email to multiple people DONE
# - Save email_receivers as .env DONE
# - delete video files after drive upload - use function from clean_old_files - make sure function runs once a day DONE
# - multi-thread I/O operations to reduce lag DONE
# - adjust video capture length after motion detection DONE
# - consider ignoring any motion made within first 1 minute (setup of camera may cause motion) DONE

"""Fixes I need to make after testing"""
# - configure raspberry pi and transfer code onto it
# - consider configuring program to run automatically on startup (after turning the power on for the raspberry pi)

"""Things I may want to consider"""



import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2 as cv
import imutils
import threading
import time
from datetime import datetime
from email_module import send_email
from drive_module import upload_video
from clean_old_files import cleanup_old_videos
from dotenv import load_dotenv

# adjust depending on how long you want the camera to wait before 
# starting capture after starting program (in seconds)
STANDBY_TIME = 60

# Load environment variables from .env file
load_dotenv()
# Set the receivers of the email as a list of strings
email_receivers = os.environ.get('EMAIL_RECEIVERS').split(',')

# Function clean up old videos asynchronously
def cleanup_old_videos_async(directory, retention_days):
    threading.Thread(target=cleanup_old_videos, args=(directory, retention_days)).start()
# Check and delete videos last modified before the past 7 days
cleanup_old_videos('saved_footage/', 7)

video_cap = cv.VideoCapture(0) # capture from webcam
static_frame = None

# Define the codec and create VideoWriter object
fourcc = cv.VideoWriter_fourcc(*'XVID')
out = None
motion_detected = False
video_timer = 0 #to track current video duration
camera_timer = 0 #tracks how long the camera has been running for
current_video_name = None #store the current file_name of the video
current_video_path = None #store the current path for the video
no_motion_grace = 0 #tracks how long it has been since a motion was detected last


# subtract images
def subtract_images(image1, image2):
    diff = cv.absdiff(image1, image2)
    _, thresh = cv.threshold(diff, 50, 255, cv.THRESH_BINARY)
    return diff, thresh

# Function to upload video asynchronously
def upload_video_async(path, name):
    threading.Thread(target=upload_video, args=(path, name)).start()

# Function to send email asynchronously
def send_email_async(email_receivers, time_detected):
    threading.Thread(target=send_email, args=(email_receivers, time_detected)).start()


# Main loop
while True:

    # waits STANDBY_TIME (seconds) to start camera to prevent false positives 
    # (ie. time after stating camera and leaving room - unnecessary to capture)
    if camera_timer == 0:
        time.sleep(STANDBY_TIME)

    success, frame = video_cap.read()
    if not success:
        print("!!!error: could not read from camera!!!")
        break

    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # captures new static frame every 140 frames (10 secs)
    if camera_timer % 140 == 0:
        static_frame = gray_frame

    # get the subtract frames
    diff, thresh = subtract_images(static_frame, gray_frame)
    dilated_image = cv.dilate(thresh, None, iterations=2)

    # get contours
    cnts = cv.findContours(dilated_image.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    # resets motion_detected
    motion_detected = False
    
    # iterate the contours
    for c in cnts:
        if cv.contourArea(c) < 700:
            continue
        
        if cv.contourArea(c) >= 700:
            motion_detected = True
    
        # get the bounding box coordinates
        (x, y, w, h) = cv.boundingRect(c)
        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv.imshow("Security Camera", frame)

    if video_timer > 0 and motion_detected == False:
        no_motion_grace += 1
    if motion_detected == True:
        no_motion_grace = 0
    
    # checks if a recording hasn't started yet and if motion has been detected then start new recording
    if video_timer == 0 and motion_detected == True:
        time_detected = datetime.now()
        print("motion detected!!! - recording started")

        #send an email to notify a motion has been detected in the room
        send_email_async(email_receivers, time_detected)

        current_video_path = "saved_footage/"
        current_video_name = "motion-detected_" + time_detected.strftime("%Y-%m-%d_%H-%M-%S") + ".avi"
        out = cv.VideoWriter(current_video_path + current_video_name, fourcc, 14.0, (640,  480))
        
    # write frames while motion is detected 
    # or there hasn't been a motion in less than 210 frames (15 seconds) while video is running
    if motion_detected == True or (video_timer > 0 and no_motion_grace < 210):
        out.write(frame)
        video_timer += 1

    # if there hasn't been any motion for 210 frames then recording stops
    if no_motion_grace == 210:
        out.release()
        out = None
        upload_video_async(current_video_path, current_video_name) # upload video in background
        no_motion_grace = 0
        video_timer = 0

    # exit if any key is pressed
    if cv.waitKey(1) & 0xFF != 255:
        break
    time.sleep(0.05)

    camera_timer += 1

video_cap.release()
if out is not None:
    out.release()  # Release the VideoWriter if it was initialized
    upload_video_async(current_video_path, current_video_name)
cv.destroyAllWindows()