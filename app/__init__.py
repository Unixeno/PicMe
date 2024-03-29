from flask import Flask, send_from_directory, redirect
from .views import (
    auth,
    admin,
    user
)
from .models import db
from flask_wtf.csrf import CSRFProtect, generate_csrf

instance = Flask(__name__, instance_relative_config=True, template_folder='templates')
csrf = CSRFProtect()
csrf.init_app(instance)

instance.config.from_pyfile('config.py')

instance.register_blueprint(auth.bp)
instance.register_blueprint(admin.bp)
instance.register_blueprint(user.bp)


@instance.before_request
def before_request():
    db.init(instance.config.get('DB_NAME'), host=instance.config.get('DB_HOST'),
            user=instance.config.get('DB_USER'), password=instance.config.get('DB_PASS'))
    db.connect(reuse_if_open=True)


@instance.after_request
def after_request(response):
    if not db.is_closed():
        db.close()
    return response


@instance.route('/upload/<year>/<month>/<path:filename>')
def uploaded_file(year, month, filename):
    return send_from_directory('../upload/%s/%s/'% (year, month), filename)


@instance.route('/', methods=['GET'])
def index():
    return redirect('/user')
