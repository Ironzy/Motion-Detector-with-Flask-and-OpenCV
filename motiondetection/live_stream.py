from flask import (
    Blueprint, Response
)
from werkzeug.exceptions import abort

from imutils.video import VideoStream
import imutils

import cv2

bp = Blueprint('live_stream', __name__, url_prefix='/live_stream')

def gen_frames():
    camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            # resize the frame
            frame = imutils.resize(frame, width=500)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@bp.route('/live_stream')
def live_stream():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



