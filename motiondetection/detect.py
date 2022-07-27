from flask import (
    Blueprint, render_template
)
from werkzeug.exceptions import abort

bp = Blueprint('detect', __name__)

@bp.route('/detect')
def detect():
    return render_template('detect.html')



