from flask import Blueprint, jsonify, abort, request
import sqlalchemy
from ..models import Tweet, User, db, likes_table

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
        username=request.json['username'],
        password=scramble(request.json['password'])
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
    u = User.query.get_or_404(id)
    try:
        db.session.delete(u)  # prepare DELETE statement
        db.session.commit()  # execute DELETE statement
        return jsonify(True)
    except:
        # something went wrong :(
        return jsonify(False)


@bp.route('/<int:id>', methods=['PATCH'])
def update(id: int):
    flag = False
    try:
        updates = {}
        if 'username' in request.json:
            updates['username'] = request.json['username']
            flag = True
        if 'password' in request.json:
            updates['password'] = scramble(request.json['password'])
            flag = True
        if flag == False:
            return jsonify('no change')
        try:
            # prepare UPDATE statement
            db.session.query(User).filter(User.id == id).update(
                updates, synchronize_session=False)
            db.session.commit()  # execute UPDATE statement
            return jsonify(True)
        except:
            # something went wrong :(
            return jsonify(False)
    except:
        # something went wrong :(
        return jsonify(None)


@bp.route('/<int:id>/liked_tweets', methods=['GET'])
def liking_users(id: int):
    u = User.query.get_or_404(id)
    liked = []
    for l in u.liked_tweets:
        liked.append(l.serialize())
    return jsonify(liked)


@bp.route('/<int:id>/likes', methods=['POST'])
def like(id: int):
    if 'tweet_id' not in request.json:
        return abort(400)
    # if tweek has already beel liked return
    r = sqlalchemy.select(likes_table).where(likes_table.c.user_id == id).where(
        likes_table.c.tweet_id == request.json['tweet_id'])
    chk = db.session.query(r.exists()).scalar()
    if chk:
        return jsonify(False)
    # check user exists
    u = User.query.get_or_404(id)
    # check tweet exists
    t = Tweet.query.get_or_404(request.json['tweet_id'])
    try:
        stmt = sqlalchemy.insert(likes_table).values(
            user_id=id, tweet_id=request.json['tweet_id'])
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(True)
    except:
        return jsonify(None)


@bp.route('/<int:id>/likes', methods=['DELETE'])
def unlike(id: int):
    # check user exists
    u = User.query.get_or_404(id)
    # check tweet exists
    t = Tweet.query.get_or_404(request.json['tweet_id'])
    try:
        stmt = sqlalchemy.delete(likes_table).where(
            sqlalchemy.and_(
                likes_table.c.user_id == id,
                likes_table.c.tweet_id == request.json['tweet_id']
            )
        )
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(True)
    except:
        return jsonify(False)
