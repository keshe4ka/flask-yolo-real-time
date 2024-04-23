# todo: save logpass to db in future
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import engine
from app.models import User

auth = HTTPBasicAuth()
users = {
    "artem": generate_password_hash("password"),
    "vlad": generate_password_hash("password")
}


@auth.verify_password
def verify_password(username, password):
    # with Session(engine) as db:
    #     user = db.query(User).filter_by(username=username).first()
    # if not user:
    #     return
    # if not check_password_hash(user.password_hash, password):
    #     return
    if username in users and \
            check_password_hash(users.get(username), password):
        return username
