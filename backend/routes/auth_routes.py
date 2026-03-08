from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from backend.extensions import db
from backend.models.user_model import User
from backend.models.patient_model import Patient
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)


# =========================
# REGISTER
# =========================
@auth_bp.route('/register', methods=['POST'])
def register():
    """Patient registration"""
    try:
        data = request.get_json()

        # Check if user exists
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email already exists'}), 400

        # Create user
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            role='patient'
        )

        user.set_password(data.get('password'))

        db.session.add(user)
        db.session.flush()  # Get user ID without committing

        # Create patient profile
        patient = Patient(
            user_id=user.id,
            name=data.get('name'),
            phone=data.get('phone'),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            address=data.get('address'),
            blood_group=data.get('blood_group'),
            emergency_contact=data.get('emergency_contact')
        )

        db.session.add(patient)
        db.session.commit()

        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# =========================
# LOGIN
# =========================
@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):

            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 403

            # IMPORTANT FIX:
            # Identity must be STRING for JWT
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={
                    'role': user.role
                },
                expires_delta=timedelta(hours=1)
            )

            refresh_token = create_refresh_token(
                identity=str(user.id)
            )

            # Profile data
            profile = None

            if user.role == 'patient' and user.patient_profile:
                profile = user.patient_profile.to_dict()

            elif user.role == 'doctor' and user.doctor_profile:
                profile = user.doctor_profile.to_dict()

            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict(),
                'profile': profile
            }), 200

        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =========================
# REFRESH TOKEN
# =========================
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()

        # Convert string → int
        user = User.query.get(int(current_user_id))

        if not user or not user.is_active:
            return jsonify({
                'error': 'User not found or inactive'
            }), 401

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'role': user.role
            }
        )

        return jsonify({
            'access_token': access_token
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =========================
# PROFILE
# =========================
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()

        # Convert string → int
        user = User.query.get(int(current_user_id))

        if not user:
            return jsonify({'error': 'User not found'}), 404

        profile = None

        if user.role == 'patient' and user.patient_profile:
            profile = user.patient_profile.to_dict()

        elif user.role == 'doctor' and user.doctor_profile:
            profile = user.doctor_profile.to_dict()

        return jsonify({
            'user': user.to_dict(),
            'profile': profile
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =========================
# LOGOUT
# =========================
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout endpoint
    JWT is stateless so logout is client-side
    """
    return jsonify({
        'message': 'Logged out successfully'
    }), 200