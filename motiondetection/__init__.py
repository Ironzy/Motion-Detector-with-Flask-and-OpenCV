import os

from flask import Flask

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path, 'server_room_access.sqlite'),
		UPLOAD_FOLDER = os.path.join('static', 'image_res'),
	)

	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)

	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# register the database commands
	from . import db 

	db.init_app(app)

	# apply the blueprints to the app

	from . import index
	app.register_blueprint(index.bp)
	app.add_url_rule('/', endpoint='index')

	from . import live_stream
	app.register_blueprint(live_stream.bp)

	from . import detect
	app.register_blueprint(detect.bp)

	from . import video_feed
	app.register_blueprint(video_feed.bp)

	from . import access_log
	app.register_blueprint(access_log.bp)

	return app