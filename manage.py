from app.models import *
from instance.config import DB_HOST, DB_PASS, DB_USER, DB_NAME
import hashlib
import getpass

if __name__ == '__main__':
    print("setup script")
    email = input("admin user email:")
    print("admin user password:", end='')
    password = getpass.getpass()

    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf8'))
    password_hash = sha256.hexdigest()

    db.init(DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASS)
    db.connect()
    db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
    Storage.drop_table()
    Group.drop_table()
    User.drop_table()
    Images.drop_table()
    db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
    db.execute_sql("set session sql_mode='NO_AUTO_VALUE_ON_ZERO,NO_AUTO_CREATE_USER';")
    Storage.create_table()
    Storage.create(id=0, url_prefix='http://127.0.0.1:5000/', storage_name='默认存储', backend_type='local',
                   backend_config='{"local":"upload"}')

    Group.create_table()

    Group.insert(id=0, backend_strategy=Storage.get_by_id(0)).execute()

    User.create_table()
    User.create(email=email, password=password_hash)

    Images.create_table()
