from flask import (
    Blueprint, Response
)
from werkzeug.exceptions import abort

from motiondetection.db import get_db

from imutils.video import VideoStream
#import argparse
import datetime
import imutils
import time
import os

import cv2

bp = Blueprint('video_feed', __name__, url_prefix='/video_feed')

def log_access(db, access_date, image_url):
    db.execute(
            'INSERT INTO access_log (access_date, image_url)'
            ' VALUES (?, ?)',
            (access_date, image_url)
        )            
    db.commit()

def gen_frames(db):
    camera = cv2.VideoCapture(0)

    firstFrame = None
    avg = None

    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            text = "Unoccupied"
            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # if the first frame is None, initialize it
            '''if firstFrame is None:
                firstFrame = gray
                continue'''

            # if the average frame is None, initialize it
            if avg is None:
                print("[INFO] starting background model...")
                avg = gray.copy().astype("float")
                #vs.close()
                continue

            # compute the absolute difference between the current frame and
            # first frame
            '''frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]'''


            cv2.accumulateWeighted(gray, avg, 0.5)
            frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

            thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]

            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < 5000:
                    continue

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"

            # draw the text and timestamp on the frame
            cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)


            if text == 'Occupied':
                cv2.imwrite(os.path.join('motiondetection/static/image_res' , 'img'+str(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"))+'.jpg'), frame)
                access_date = str(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"))
                image_url = 'img'+str(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"))+'.jpg'
                log_access(db, access_date, image_url)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@bp.route('/video_feed')
def video_feed():
    db = get_db()
    return Response(gen_frames(db), mimetype='multipart/x-mixed-replace; boundary=frame')



