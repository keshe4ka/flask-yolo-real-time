# todo: save logpass to db in future
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

auth = HTTPBasicAuth()
users = {
    "artem": generate_password_hash("password"),
    "vlad": generate_password_hash("password")
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username
