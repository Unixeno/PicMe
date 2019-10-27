from flask import Blueprint, request, render_template, url_for, session
from flask import redirect, jsonify, current_app, g
from ..util.storage import storage_factory
from ..models import Images, User
from ..util.helper import bytes_to_human

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.before_request
def before_request():
    if session.get('user_id'):
        user = User()
        g.userinfo = user.get_user(session.get('user_id'))
    else:
        return redirect(url_for('auth.login'))


@bp.route('/')
def index():
    return render_template('user/index.html')


@bp.route('/images')
def images():
    user_images = Images().fetch_user_image(g.userinfo.id)
    for image in user_images:
        storage = storage_factory(image.backend_strategy)
        image.image_path = storage.get_full_path(image.path)

    return render_template('user/images.html', images=user_images)


@bp.route('/userinfo')
def userinfo():
    return render_template('user/userinfo.html', bytes_to_human=bytes_to_human)


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


@bp.route('/image_info/<image_id>', methods=['GET'])
def get_image_info(image_id):
    image_info = Images.get()


@bp.route('/group')
def group():
    return render_template('user/group.html')


@bp.route('/user')
def user():
    return render_template('user/user.html')


@bp.route('/get_img_info')
def get_img_info():
    return jsonify({'err': 0})
