from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from celery import Celery
import redis

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
celery = Celery()

# Redis client for caching
redis_client = None

def init_redis(app):
    global redis_client
    redis_client = redis.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
        decode_responses=True
    )
    return redis_client

# Add this to handle integer subject
@jwt.user_identity_loader
def user_identity_lookup(user):
    return str(user)  # Convert to string

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    from backend.models.user_model import User
    identity = jwt_data["sub"]
    return User.query.filter_by(id=int(identity)).one_or_none()