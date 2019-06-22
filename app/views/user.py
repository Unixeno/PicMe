from flask import Blueprint, request, render_template, url_for, session
from flask import redirect, jsonify, current_app, g
from ..util.storage import storage_factory
from ..models import Storage, Images, User
from ..util.helper import bytes_to_human

bp = Blueprint('user', __name__, url_prefix='/user', template_folder='../templates/user')


@bp.before_request
def before_request():
    if session.get('user_id'):
        user = User()
        g.userinfo = user.get_user(session.get('user_id'))
    else:
        return redirect(url_for('auth.login'))


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/images')
def images():
    images = Images().fetch_user_image(g.userinfo.id)
    for image in images:
        storage = storage_factory(image.backend_strategy)
        image.image_path = storage.get_full_path(image.path)

    return render_template('images.html', images=images)


@bp.route('/userinfo')
def userinfo():
    return render_template('userinfo.html', bytes_to_human=bytes_to_human)


@bp.route('/upload', methods=['POST'])
def upload():
    if request.files['image']:
        file = request.files['image']
        if file.filename == '':
            return jsonify({'err': 1, 'info': '请选择图片'})
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() \
                not in current_app.config['ALLOWED_EXTENSIONS']:
            return jsonify({'err': 2, 'info': '无效的文件扩展名'})
        file.seek(0, 2)
        file_length = file.tell()
        file.seek(0)

        storage = storage_factory(g.userinfo.user_group.backend_strategy)
        link, path = storage.store(file)
        image = Images()
        image.save_image(user_id=g.userinfo.id, size=file_length,
                         backend_strategy=g.userinfo.user_group.backend_strategy, path=path)

        return jsonify({'err': 0, 'link': link, 'local_name': file.filename, 'size': file_length})


