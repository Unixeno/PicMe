from flask import Blueprint, request, render_template, redirect, url_for, jsonify, g
from ..models import Storage, DoesNotExist, User
from ..util.storage import QiniuStorage, LocalStorage
from flask import session

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.before_request
def before_request():
    if session.get('user_id'):
        g.userinfo = User().get_user(session.get('user_id'))
        if g.userinfo.role == 0:
            return
    else:
        return redirect(url_for('auth.login'))


@bp.route('/')
def index():
    return render_template('admin/index.html')


@bp.route('/user')
def user():
    return render_template('index.html')


@bp.route('/group')
def group():
    pass


@bp.route('/storage')
def storage():
    storages = Storage.get_all_storage()
    return render_template('admin/storage.html', storages=storages)


@bp.route('/update_storage', methods=['POST'])
def update_storage():
    try:
        storage = Storage.get_by_id(request.form['storage_id'])
    except DoesNotExist:
        return jsonify({'err': 1, 'info': '无效的存储id'})
    storage.storage_name = request.form['storage_name']
    storage.url_prefix = request.form['url_prefix']
    if request.form['storage_type'] == 'local':
        storage.backend_type = 'local'
        storage.backend_config = LocalStorage.build_config(request.form)
        storage.save()
        return jsonify({'err': 0})
    elif request.form['storage_type'] == 'qiniu':
        storage.backend_type = 'qiniu'
        storage.backend_config = QiniuStorage.build_config(request.form)
        storage.save()
        return jsonify({'err': 0})
    return jsonify({'err': 1, 'info': '不支持的存储类型'})