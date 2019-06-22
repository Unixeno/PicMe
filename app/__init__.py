from flask import Flask, send_from_directory
from app.views import auth
from app.views import user
from .models import db
from flask_wtf.csrf import CSRFProtect, generate_csrf

instance = Flask(__name__, instance_relative_config=True)
csrf = CSRFProtect()
csrf.init_app(instance)

instance.config.from_pyfile('config.py')

instance.register_blueprint(auth.bp)
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
    # csrf_token = generate_csrf()
    # response.set_cookie("csrf_token", csrf_token)
    return response


@instance.route('/upload/<year>/<month>/<path:filename>')
def uploaded_file(year, month, filename):
    return send_from_directory('../upload/%s/%s/'% (year, month), filename)


