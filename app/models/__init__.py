from peewee import *
import datetime
import hashlib
from playhouse.shortcuts import model_to_dict


db = MySQLDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Storage(BaseModel):
    id = AutoField(primary_key=True)
    url_prefix = CharField(max_length=128)

    backend_type = CharField(max_length=16)
    backend_config = CharField(max_length=1024)


class Group(BaseModel):
    id = AutoField(primary_key=True)
    limit = BigIntegerField(default=0)          # 数量限制
    file_size = IntegerField(default=0)         # 图片尺寸限制
    backend_strategy = ForeignKeyField(Storage)


class User(BaseModel):
    id = AutoField(primary_key=True)
    email = CharField(max_length=64)
    password = FixedCharField(max_length=64)
    user_group = ForeignKeyField(Group, 'id', default=0)
    size = BigIntegerField(default=0)            # 已用空间
    image_count = IntegerField(default=0)
    role = SmallIntegerField(default=1)  # 角色，0=管理员，1=用户
    reg_date = DateTimeField(default=datetime.datetime.now, formats='%Y-%m-%d %H:%M:%S')

    def login(self, email, password):
        sha256 = hashlib.sha256()
        sha256.update(password.encode('utf8'))
        password_hash = sha256.hexdigest()
        try:
            user_id = self.select(User.id).where((User.email == email) & (User.password == password_hash)).get()
            return user_id.id
        except DoesNotExist:
            return None

    def get_user(self, user_id):
        userinfo = self.select(User, Group).join(Group, on=(User.user_group == Group.id)).\
            where(User.id == user_id).get()
        return userinfo

    def user_exist(self, email):
        try:
            self.get(User.email == email)
        except DoesNotExist:
            return False
        return True

    def register(self, email, password, role=1, user_group=0):
        sha256 = hashlib.sha256()
        sha256.update(password.encode('utf8'))
        password_hash = sha256.hexdigest()
        self.create(email=email, password=password_hash, role=role, user_group=user_group)


class Images(BaseModel):
    id = AutoField(primary_key=True)
    user_id = ForeignKeyField(User)
    size = IntegerField()
    backend_strategy = ForeignKeyField(Storage)
    path = CharField(max_length=128)
    deleted = BooleanField(default=False)
    upload_time = DateTimeField(default=datetime.datetime.now, formats='%Y-%m-%d %H:%M:%S')

    def save_image(self, user_id, size, backend_strategy, path):
        with db.atomic():
            # 更新用户的容量
            User.update(size=User.size + size, image_count=User.image_count + 1).where(User.id == user_id).execute()
            self.create(user_id=user_id, size=size, backend_strategy=backend_strategy, path=path)

    def fetch_user_image(self, user_id):
        images = self.select().where((Images.user_id == user_id) & (Images.deleted == 0))

        return images

