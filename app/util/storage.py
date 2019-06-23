from app.models import Storage as StorageModel
import datetime
import json
import random
import hashlib
import mimetypes
import os
from werkzeug.utils import secure_filename
from flask import g, current_app
import qiniu


def storage_factory(backend_strategy):
    if getattr(g, 'storage', None) is None:
        g.storage = {}
    if backend_strategy in g.storage:
        return g.storage[backend_strategy]

    storage_strategy = StorageModel.get_by_id(backend_strategy)

    if storage_strategy.backend_type == 'local':
        g.storage[backend_strategy] = LocalStorage(storage_strategy)
    elif storage_strategy.backend_type == 'qiniu':
        g.storage[backend_strategy] = QiniuStorage(storage_strategy)

    return g.storage[backend_strategy]


class StorageBase(object):
    def __init__(self, strategy: StorageModel):
        self._url_prefix = strategy.url_prefix
        if strategy.backend_config != '':
            self._backend_config = json.loads(strategy.backend_config, encoding='utf8')
        else:
            self._backend_config = {}

    def store(self, file):
        pass

    def get_full_path(self, path):
        return self._url_prefix + path

    @staticmethod
    def hash_filename(filename):
        current_time = datetime.datetime.now()
        sha1 = hashlib.sha1()
        sha1.update(secure_filename(filename).encode('utf8'))
        sha1.update(('%s%s-%f' % (current_time.year, current_time.month, random.random())).encode('ascii'))
        return "%s.%s" % (sha1.hexdigest(), filename.rsplit('.', 1)[1].lower())

    @staticmethod
    def path_to_url(path: str):
        return path.replace(r'\\', '/').replace('\\', '/')

    @staticmethod
    def build_config(form):
        return "{}"


class LocalStorage(StorageBase):
    def store(self, file):
        # local_path = self._backend_config['local']
        current_time = datetime.datetime.now()
        current_year = "%d" % current_time.year
        current_month = "%02d" % current_time.month
        file_path = os.path.join(self._backend_config['local'], current_year, current_month,
                                 StorageBase.hash_filename(file.filename))
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        return self._url_prefix + StorageBase.path_to_url(file_path), StorageBase.path_to_url(file_path)

    def get_full_path(self, path):
        return self._url_prefix + path

    @staticmethod
    def build_config(form):
        return json.dumps({
            "local": form['local-local']
        })


class QiniuStorage(StorageBase):
    def __init__(self, strategy: StorageModel):
        super(QiniuStorage, self).__init__(strategy)
        self._q = qiniu.Auth(self._backend_config['qiniu_accesskey'],
                             self._backend_config['qiniu_secretkey'])

    def store(self, file):
        current_time = datetime.datetime.now()
        current_year = "%d" % current_time.year
        current_month = "%02d" % current_time.month
        file_path = '/'.join([current_year, current_month, StorageBase.hash_filename(file.filename)])
        upload_token = self._q.upload_token(self._backend_config['qiniu_bucket'], file_path, 600)
        ret, info = qiniu.put_data(upload_token, file_path, file, mime_type=mimetypes.guess_type(file.filename)[0])

        return self.get_full_path(file_path), file_path

    def build_config(form):
        return json.dumps({
            "qiniu_accesskey": form['qiniu-ak'],
            "qiniu_secretkey": form['qiniu-sk'],
            "qiniu_bucket": form['qiniu-bucket']
        })
