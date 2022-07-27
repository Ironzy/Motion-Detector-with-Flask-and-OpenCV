from flask import (
    Blueprint, render_template, request
)
from werkzeug.exceptions import abort

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

