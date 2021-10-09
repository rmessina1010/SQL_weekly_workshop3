from flask import Blueprint, jsonify, abort, request
from ..models import User, db
import hashlib
import secrets


def scramble(password: str):
    """Hash and salt the given password"""
    salt = secrets.token_hex(16)
    return hashlib.sha512((password + salt).encode('utf-8')).hexdigest()


bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('', methods=['GET'])  # decorator takes path and list of HTTP verbs
def index():
    users = User.query.all()  # ORM performs SELECT query
    result = []
    for u in users:
        result.append(u.serialize())  # build list of Tweets as dictionaries
    return jsonify(result)  # return JSON response


@bp.route('/<int:id>', methods=['GET'])
def show(id: int):
    u = User.query.get_or_404(id)
    # return jsonify({"test": 1})
    return jsonify(u.serialize())


@bp.route('', methods=['POST'])  # decorator takes path and list of HTTP verbs
def create():
    # req body must contain username and password
    if 'username' not in request.json or 'password' not in request.json:
        return abort(400)
    if len(request.json['username']) < 3 or len(request.json['password']) < 8:
        return abort(400)
    u = User(
        request.json['username'],
        scramble(request.json['password'])
    )
    try:
        db.session.add(u)  # prepare CREATE statement
        db.session.commit()  # execute CREATE statement
        return jsonify(True)
    except:
        # something went wrong :(
        return jsonify(False)


# decorator takes path and list of HTTP verbs
@bp.route('/<int:id>', methods=['DELETE'])
def delete(id: int):
    return jsonify(False)


@bp.route('', methods=['PUT'])
def show():
    return jsonify({"test": 1})
