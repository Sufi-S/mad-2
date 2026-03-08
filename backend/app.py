from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.extensions import db, bcrypt, jwt, celery, init_redis


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # Initialize extensions

    CORS(app)

    db.init_app(app)

    bcrypt.init_app(app)

    jwt.init_app(app)

    # Redis

    init_redis(app)

    # Celery

    celery.conf.update(app.config)

    # Register Blueprints

    from backend.routes.auth_routes import auth_bp
    from backend.routes.admin_routes import admin_bp
    from backend.routes.doctor_routes import doctor_bp
    from backend.routes.patient_routes import patient_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')

    app.register_blueprint(patient_bp, url_prefix='/api/patient')


    # Health Check

    @app.route('/health')

    def health_check():

        return jsonify({

            'status': 'healthy',

            'redis': check_redis_connection(),

            'celery': check_celery_worker()

        })


    # Create Database

    with app.app_context():

        from backend.database.init_db import init_database

        init_database()


    return app



def check_redis_connection():

    try:

        from backend.extensions import redis_client

        redis_client.ping()

        return True

    except:

        return False



def check_celery_worker():

    try:

        inspect = celery.control.inspect()

        active = inspect.active()

        return bool(active)

    except:

        return False



app = create_app()


if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0", port=5000)