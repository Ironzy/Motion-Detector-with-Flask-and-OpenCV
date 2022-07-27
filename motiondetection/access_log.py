from flask import (
    Blueprint, render_template, current_app
)
from werkzeug.exceptions import abort

from motiondetection.db import get_db

import os

bp = Blueprint('access_log', __name__)

@bp.route('/access_log')
def access_log():
    db = get_db()
    logs = db.execute(
        'SELECT * FROM access_log GROUP BY created  ORDER BY created DESC'
        ).fetchall()
    return render_template('logs.html', logs=logs, path=current_app.config['UPLOAD_FOLDER'])



